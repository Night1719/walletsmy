#!/usr/bin/env python3
"""
LDAP менеджер для BG Survey Platform
"""

import os
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from typing import List, Dict, Optional

class LDAPManager:
    def __init__(self):
        self.server_url = os.environ.get('LDAP_SERVER', 'ldap://localhost:389')
        self.base_dn = os.environ.get('LDAP_BASE_DN', 'dc=example,dc=com')
        self.bind_dn = os.environ.get('LDAP_BIND_DN', '')
        self.bind_password = os.environ.get('LDAP_BIND_PASSWORD', '')
        self.user_search_base = os.environ.get('LDAP_USER_SEARCH_BASE', '')
        self.group_search_base = os.environ.get('LDAP_GROUP_SEARCH_BASE', '')
        
    def test_connection(self) -> Dict[str, any]:
        """Тестирует подключение к LDAP серверу"""
        try:
            server = Server(self.server_url, get_info=ALL)
            conn = Connection(server, user=self.bind_dn, password=self.bind_password)
            
            if not conn.bind():
                return {
                    'success': False,
                    'error': f'Ошибка аутентификации: {conn.result}'
                }
            
            # Тестируем поиск
            search_filter = '(objectClass=person)'
            conn.search(
                self.user_search_base or self.base_dn,
                search_filter,
                SUBTREE,
                attributes=['cn', 'mail', 'sAMAccountName']
            )
            
            conn.unbind()
            
            return {
                'success': True,
                'message': 'Подключение к LDAP успешно',
                'server': self.server_url,
                'base_dn': self.base_dn
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка подключения: {str(e)}'
            }
    
    def search_users(self, query: str = '', max_results: int = 100) -> List[Dict]:
        """Поиск пользователей в LDAP"""
        try:
            server = Server(self.server_url, get_info=ALL)
            conn = Connection(server, user=self.bind_dn, password=self.bind_password)
            
            if not conn.bind():
                return []
            
            # Формируем фильтр поиска
            if query:
                search_filter = f'(&(objectClass=person)(|(cn=*{query}*)(mail=*{query}*)(sAMAccountName=*{query}*)))'
            else:
                search_filter = '(objectClass=person)'
            
            # Выполняем поиск
            conn.search(
                self.user_search_base or self.base_dn,
                search_filter,
                SUBTREE,
                attributes=['cn', 'mail', 'sAMAccountName', 'givenName', 'sn', 'department', 'title'],
                size_limit=max_results
            )
            
            users = []
            for entry in conn.entries:
                user_data = {
                    'cn': str(entry.cn[0]) if entry.cn else '',
                    'mail': str(entry.mail[0]) if entry.mail else '',
                    'sAMAccountName': str(entry.sAMAccountName[0]) if entry.sAMAccountName else '',
                    'givenName': str(entry.givenName[0]) if entry.givenName else '',
                    'sn': str(entry.sn[0]) if entry.sn else '',
                    'department': str(entry.department[0]) if entry.department else '',
                    'title': str(entry.title[0]) if entry.title else '',
                    'dn': str(entry.entry_dn)
                }
                users.append(user_data)
            
            conn.unbind()
            return users
            
        except Exception as e:
            print(f"❌ Ошибка поиска пользователей LDAP: {e}")
            return []
    
    def import_users(self, user_dns: List[str]) -> Dict[str, any]:
        """Импортирует пользователей из LDAP в систему"""
        try:
            server = Server(self.server_url, get_info=ALL)
            conn = Connection(server, user=self.bind_dn, password=self.bind_password)
            
            if not conn.bind():
                return {
                    'success': False,
                    'error': 'Ошибка аутентификации LDAP'
                }
            
            imported_users = []
            errors = []
            
            for user_dn in user_dns:
                try:
                    # Получаем данные пользователя
                    conn.search(
                        user_dn,
                        '(objectClass=person)',
                        SUBTREE,
                        attributes=['cn', 'mail', 'sAMAccountName', 'givenName', 'sn']
                    )
                    
                    if conn.entries:
                        entry = conn.entries[0]
                        user_data = {
                            'username': str(entry.sAMAccountName[0]) if entry.sAMAccountName else str(entry.cn[0]),
                            'email': str(entry.mail[0]) if entry.mail else '',
                            'first_name': str(entry.givenName[0]) if entry.givenName else '',
                            'last_name': str(entry.sn[0]) if entry.sn else '',
                            'ldap_dn': user_dn
                        }
                        imported_users.append(user_data)
                    else:
                        errors.append(f'Пользователь не найден: {user_dn}')
                        
                except Exception as e:
                    errors.append(f'Ошибка обработки {user_dn}: {str(e)}')
            
            conn.unbind()
            
            return {
                'success': True,
                'imported_users': imported_users,
                'errors': errors,
                'total_imported': len(imported_users)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка импорта: {str(e)}'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, any]:
        """Аутентификация пользователя через LDAP"""
        try:
            server = Server(self.server_url, get_info=ALL)
            
            # Ищем пользователя
            conn = Connection(server, user=self.bind_dn, password=self.bind_password)
            if not conn.bind():
                return {
                    'success': False,
                    'error': 'Ошибка подключения к LDAP'
                }
            
            # Поиск пользователя
            search_filter = f'(&(objectClass=person)(sAMAccountName={username}))'
            conn.search(
                self.user_search_base or self.base_dn,
                search_filter,
                SUBTREE,
                attributes=['cn', 'mail', 'sAMAccountName', 'givenName', 'sn']
            )
            
            if not conn.entries:
                return {
                    'success': False,
                    'error': 'Пользователь не найден'
                }
            
            user_dn = str(conn.entries[0].entry_dn)
            conn.unbind()
            
            # Пытаемся аутентифицировать пользователя
            user_conn = Connection(server, user=user_dn, password=password)
            if not user_conn.bind():
                return {
                    'success': False,
                    'error': 'Неверный пароль'
                }
            
            # Получаем данные пользователя
            user_conn.search(
                user_dn,
                '(objectClass=person)',
                SUBTREE,
                attributes=['cn', 'mail', 'sAMAccountName', 'givenName', 'sn']
            )
            
            if user_conn.entries:
                entry = user_conn.entries[0]
                user_data = {
                    'username': str(entry.sAMAccountName[0]) if entry.sAMAccountName else str(entry.cn[0]),
                    'email': str(entry.mail[0]) if entry.mail else '',
                    'first_name': str(entry.givenName[0]) if entry.givenName else '',
                    'last_name': str(entry.sn[0]) if entry.sn else '',
                    'ldap_dn': user_dn
                }
                
                user_conn.unbind()
                
                return {
                    'success': True,
                    'user_data': user_data
                }
            
            user_conn.unbind()
            return {
                'success': False,
                'error': 'Не удалось получить данные пользователя'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка аутентификации: {str(e)}'
            }

# Глобальный экземпляр
ldap_manager = LDAPManager()