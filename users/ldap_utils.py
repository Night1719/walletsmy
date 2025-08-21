from ldap3 import Server, Connection, ALL, SUBTREE
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class LDAPImporter:
    """Класс для импорта пользователей из LDAP"""
    
    def __init__(self, config):
        self.config = config
        self.server_uri = config.get('server_uri')
        self.bind_dn = config.get('bind_dn')
        self.bind_password = config.get('bind_password')
        self.search_base = config.get('search_base')
        self.search_filter = config.get('search_filter')
        self.default_role = config.get('default_role', User.UserRole.USER)
        self.can_create_surveys = config.get('can_create_surveys', False)
    
    def test_connection(self):
        """Тестирует подключение к LDAP серверу"""
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True
            )
            
            if conn.bound:
                conn.unbind()
                return True, None
            else:
                return False, _('Не удалось привязаться к LDAP серверу')
                
        except Exception as e:
            logger.error(f"LDAP connection error: {e}")
            return False, str(e)
    
    def search_users(self):
        """Поиск пользователей в LDAP"""
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True
            )
            
            if not conn.bound:
                raise Exception(_('Не удалось привязаться к LDAP серверу'))
            
            # Поиск пользователей
            conn.search(
                search_base=self.search_base,
                search_filter=self.search_filter,
                search_scope=SUBTREE,
                attributes=[
                    'sAMAccountName', 'mail', 'givenName', 'sn',
                    'department', 'title', 'telephoneNumber', 'distinguishedName'
                ]
            )
            
            users = []
            for entry in conn.entries:
                user_data = {
                    'username': self._get_attribute(entry, 'sAMAccountName'),
                    'email': self._get_attribute(entry, 'mail'),
                    'first_name': self._get_attribute(entry, 'givenName'),
                    'last_name': self._get_attribute(entry, 'sn'),
                    'department': self._get_attribute(entry, 'department'),
                    'position': self._get_attribute(entry, 'title'),
                    'phone': self._get_attribute(entry, 'telephoneNumber'),
                    'ldap_dn': self._get_attribute(entry, 'distinguishedName')
                }
                
                # Проверяем обязательные поля
                if user_data['username'] and user_data['email']:
                    users.append(user_data)
            
            conn.unbind()
            return users
            
        except Exception as e:
            logger.error(f"LDAP search error: {e}")
            raise e
    
    def import_users(self):
        """Импортирует пользователей из LDAP"""
        imported_count = 0
        errors = []
        
        try:
            # Тестируем подключение
            connection_ok, error = self.test_connection()
            if not connection_ok:
                errors.append(f"Ошибка подключения: {error}")
                return imported_count, errors
            
            # Получаем список пользователей
            ldap_users = self.search_users()
            
            for user_data in ldap_users:
                try:
                    # Проверяем, существует ли пользователь
                    existing_user = User.objects.filter(
                        username=user_data['username']
                    ).first()
                    
                    if existing_user:
                        # Обновляем существующего пользователя
                        self._update_user(existing_user, user_data)
                        logger.info(f"Обновлен пользователь: {user_data['username']}")
                    else:
                        # Создаем нового пользователя
                        self._create_user(user_data)
                        imported_count += 1
                        logger.info(f"Импортирован пользователь: {user_data['username']}")
                
                except Exception as e:
                    error_msg = f"Ошибка импорта пользователя {user_data.get('username', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return imported_count, errors
            
        except Exception as e:
            error_msg = f"Общая ошибка импорта: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            return imported_count, errors
    
    def _create_user(self, user_data):
        """Создает нового пользователя"""
        # Генерируем временный пароль
        temp_password = self._generate_temp_password()
        
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=temp_password,
            first_name=user_data['first_name'] or '',
            last_name=user_data['last_name'] or '',
            department=user_data['department'] or '',
            position=user_data['position'] or '',
            phone=user_data['phone'] or '',
            role=self.default_role,
            can_create_surveys=self.can_create_surveys,
            is_ldap_user=True,
            ldap_dn=user_data['ldap_dn'] or ''
        )
        
        # Создаем профиль пользователя
        from .models import UserProfile
        UserProfile.objects.create(user=user)
        
        # Логируем создание пользователя
        logger.info(f"Создан пользователь {user.username} с временным паролем: {temp_password}")
        
        return user
    
    def _update_user(self, user, user_data):
        """Обновляет существующего пользователя"""
        user.email = user_data['email'] or user.email
        user.first_name = user_data['first_name'] or user.first_name
        user.last_name = user_data['last_name'] or user.last_name
        user.department = user_data['department'] or user.department
        user.position = user_data['position'] or user.position
        user.phone = user_data['phone'] or user.phone
        user.is_ldap_user = True
        user.ldap_dn = user_data['ldap_dn'] or user.ldap_dn
        user.save()
        
        return user
    
    def _get_attribute(self, entry, attr_name):
        """Безопасно получает значение атрибута LDAP"""
        try:
            if hasattr(entry, attr_name):
                value = getattr(entry, attr_name)
                if value:
                    # Если значение - список, берем первый элемент
                    if isinstance(value, list):
                        return str(value[0]) if value else ''
                    return str(value)
            return ''
        except Exception:
            return ''
    
    def _generate_temp_password(self):
        """Генерирует временный пароль"""
        import secrets
        import string
        
        # Создаем пароль с буквами, цифрами и символами
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        return password
    
    def sync_user(self, username):
        """Синхронизирует конкретного пользователя с LDAP"""
        try:
            # Ищем пользователя в LDAP
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True
            )
            
            if not conn.bound:
                raise Exception(_('Не удалось привязаться к LDAP серверу'))
            
            # Поиск конкретного пользователя
            search_filter = f"(&{self.search_filter}(sAMAccountName={username}))"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[
                    'sAMAccountName', 'mail', 'givenName', 'sn',
                    'department', 'title', 'telephoneNumber', 'distinguishedName'
                ]
            )
            
            if conn.entries:
                entry = conn.entries[0]
                user_data = {
                    'username': self._get_attribute(entry, 'sAMAccountName'),
                    'email': self._get_attribute(entry, 'mail'),
                    'first_name': self._get_attribute(entry, 'givenName'),
                    'last_name': self._get_attribute(entry, 'sn'),
                    'department': self._get_attribute(entry, 'department'),
                    'position': self._get_attribute(entry, 'title'),
                    'phone': self._get_attribute(entry, 'telephoneNumber'),
                    'ldap_dn': self._get_attribute(entry, 'distinguishedName')
                }
                
                # Обновляем пользователя
                user = User.objects.filter(username=username).first()
                if user:
                    self._update_user(user, user_data)
                    return True, _('Пользователь синхронизирован')
                else:
                    return False, _('Пользователь не найден в системе')
            else:
                return False, _('Пользователь не найден в LDAP')
            
        except Exception as e:
            logger.error(f"LDAP sync error for {username}: {e}")
            return False, str(e)
        finally:
            if 'conn' in locals() and conn.bound:
                conn.unbind()


class LDAPAuthenticator:
    """Класс для аутентификации через LDAP"""
    
    def __init__(self, server_uri, bind_dn, bind_password, search_base, search_filter):
        self.server_uri = server_uri
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.search_base = search_base
        self.search_filter = search_filter
    
    def authenticate(self, username, password):
        """Аутентифицирует пользователя через LDAP"""
        try:
            server = Server(self.server_uri, get_info=ALL)
            
            # Сначала ищем пользователя
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True
            )
            
            if not conn.bound:
                logger.error("LDAP bind failed")
                return None
            
            # Поиск пользователя
            search_filter = f"(&{self.search_filter}(sAMAccountName={username}))"
            conn.search(
                search_base=self.search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['distinguishedName']
            )
            
            if not conn.entries:
                logger.warning(f"User {username} not found in LDAP")
                return None
            
            user_dn = str(conn.entries[0]['distinguishedName'])
            conn.unbind()
            
            # Теперь пытаемся привязаться как пользователь
            user_conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            
            if user_conn.bound:
                user_conn.unbind()
                
                # Возвращаем пользователя из Django
                user = User.objects.filter(username=username).first()
                if user:
                    # Обновляем информацию из LDAP
                    importer = LDAPImporter({
                        'server_uri': self.server_uri,
                        'bind_dn': self.bind_dn,
                        'bind_password': self.bind_password,
                        'search_base': self.search_base,
                        'search_filter': self.search_filter
                    })
                    
                    importer.sync_user(username)
                    return user
                
                return None
            else:
                logger.warning(f"LDAP authentication failed for {username}")
                return None
                
        except Exception as e:
            logger.error(f"LDAP authentication error: {e}")
            return None


def get_ldap_config():
    """Получает конфигурацию LDAP из настроек Django"""
    return {
        'server_uri': getattr(settings, 'LDAP_SERVER_URI', ''),
        'bind_dn': getattr(settings, 'LDAP_BIND_DN', ''),
        'bind_password': getattr(settings, 'LDAP_BIND_PASSWORD', ''),
        'search_base': getattr(settings, 'LDAP_USER_SEARCH_BASE', ''),
        'search_filter': getattr(settings, 'LDAP_USER_SEARCH_FILTER', '')
    }


def is_ldap_enabled():
    """Проверяет, включена ли поддержка LDAP"""
    config = get_ldap_config()
    return all([
        config['server_uri'],
        config['bind_dn'],
        config['bind_password'],
        config['search_base']
    ])