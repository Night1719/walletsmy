from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///surveys.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    can_create_surveys = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    surveys = db.relationship('Survey', backref='creator', lazy=True)

class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_anonymous = db.Column(db.Boolean, default=False)
    require_auth = db.Column(db.Boolean, default=False)
    require_name = db.Column(db.Boolean, default=False)  # Новый тип опроса - ввод имени
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    questions = db.relationship('Question', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), nullable=False)  # text, multiple_choice, checkbox, rating, checkbox_grid, dropdown, date, time, file_upload
    options = db.Column(db.Text)  # JSON для вариантов ответов
    is_required = db.Column(db.Boolean, default=True)  # Обязательный вопрос
    allow_other = db.Column(db.Boolean, default=False)  # Разрешить "Другой вариант"
    other_text = db.Column(db.String(200))  # Текст для "Другой вариант"
    rating_min = db.Column(db.Integer, default=1)  # Минимальное значение рейтинга
    rating_max = db.Column(db.Integer, default=10)  # Максимальное значение рейтинга
    rating_labels = db.Column(db.Text)  # JSON для подписей рейтинга (например, ["Плохо", "Отлично"])
    grid_rows = db.Column(db.Text)  # JSON для строк сетки флажков
    grid_columns = db.Column(db.Text)  # JSON для столбцов сетки флажков
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    question_order = db.Column(db.Integer, default=0)  # Порядок вопроса
    
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    respondent_name = db.Column(db.String(200), nullable=True)  # Имя респондента для require_name опросов
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)  # User Agent браузера
    completion_time = db.Column(db.Integer, nullable=True)  # Время прохождения в секундах
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    answers = db.relationship('Answer', backref='response', lazy=True, cascade='all, delete-orphan')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_response.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)
    is_other = db.Column(db.Boolean, default=False)  # Является ли ответ "Другим вариантом"

# Новые модели для аналитики
class AnalyticsCache(db.Model):
    """Кеш для аналитических данных"""
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(200), unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON данные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

class SurveyAnalytics(db.Model):
    """Детальная аналитика по опросам"""
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)  # completion_rate, avg_time, etc.
    metric_value = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    survey = db.relationship('Survey', backref='analytics')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Вспомогательные функции для шаблонов
@app.context_processor
def utility_processor():
    def count_responses(surveys):
        """Подсчитывает общее количество ответов для списка опросов"""
        total = 0
        for survey in surveys:
            if hasattr(survey, 'responses'):
                total += len(survey.responses)
        return total
    
    def count_active_surveys(surveys):
        """Подсчитывает количество активных опросов (с ответами)"""
        count = 0
        for survey in surveys:
            if hasattr(survey, 'responses') and len(survey.responses) > 0:
                count += 1
        return count
    
    def format_date(date_obj):
        """Форматирует дату в удобочитаемый вид"""
        if date_obj:
            try:
                return date_obj.strftime('%d.%m')
            except:
                return str(date_obj)
        return '-'
    
    def get_question_icon(question_type):
        """Получает иконку для типа вопроса"""
        icons = {
            'text': 'font',
            'text_paragraph': 'align-left',
            'single_choice': 'list-ul',
            'multiple_choice': 'check-square',
            'dropdown': 'chevron-down',
            'scale': 'sliders-h',
            'rating': 'star',
            'grid': 'th',
            'checkbox_grid': 'th-list',
            'date': 'calendar',
            'time': 'clock'
        }
        return icons.get(question_type, 'question')
    
    def get_question_type_name(question_type):
        """Получает название типа вопроса"""
        names = {
            'text': 'Текст (строка)',
            'text_paragraph': 'Текст (Абзац)',
            'single_choice': 'Один из списка',
            'multiple_choice': 'Несколько из списка',
            'dropdown': 'Раскрывающийся список',
            'scale': 'Шкала',
            'rating': 'Оценка',
            'grid': 'Сетка',
            'checkbox_grid': 'Сетка из флажков',
            'date': 'Дата',
            'time': 'Время'
        }
        return names.get(question_type, 'Неизвестный тип')
    
    def from_json(json_string):
        """Преобразует JSON строку в Python объект"""
        try:
            if json_string:
                return json.loads(json_string)
            return []
        except (json.JSONDecodeError, TypeError):
            return []
    
    return {
        'count_responses': count_responses,
        'count_active_surveys': count_active_surveys,
        'format_date': format_date,
        'from_json': from_json,
        'get_question_icon': get_question_icon,
        'get_question_type_name': get_question_type_name
    }

# Регистрируем фильтр from_json отдельно
@app.template_filter('from_json')
def from_json_filter(json_string):
    """Фильтр для преобразования JSON строки в Python объект"""
    try:
        if json_string:
            return json.loads(json_string)
        return []
    except (json.JSONDecodeError, TypeError):
        return []

@app.template_filter('strftime')
def strftime_filter(date, format='%d.%m.%Y %H:%M'):
    """Фильтр для форматирования даты"""
    try:
        if date:
            return date.strftime(format)
        return ''
    except (AttributeError, TypeError):
        return ''

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Требуются права администратора', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def survey_creation_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_create_surveys:
            flash('У вас нет прав на создание опросов', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        surveys = Survey.query.all()
    else:
        surveys = Survey.query.filter_by(creator_id=current_user.id).all()
    
    return render_template('dashboard.html', surveys=surveys)

@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    surveys = Survey.query.all()
    
    # Используем SSL менеджер для получения реального статуса
    try:
        from ssl_manager import get_ssl_status
        ssl_status = get_ssl_status()
    except ImportError:
        # Fallback если SSL менеджер недоступен
        ssl_status = {
            'enabled': False,
            'certificate': None,
            'error': 'SSL менеджер недоступен'
        }
    
    return render_template('admin.html', users=users, surveys=surveys, ssl_status=ssl_status)

@app.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def admin_users():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        can_create_surveys = 'can_create_surveys' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
        else:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=is_admin,
                can_create_surveys=can_create_surveys
            )
            db.session.add(user)
            db.session.commit()
            flash('Пользователь создан успешно', 'success')
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle_admin')
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Права администратора для {user.username} изменены', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/toggle_survey_creation')
@admin_required
def toggle_survey_creation(user_id):
    user = User.query.get_or_404(user_id)
    user.can_create_surveys = not user.can_create_surveys
    db.session.commit()
    flash(f'Права на создание опросов для {user.username} изменены', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/delete')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Нельзя удалить самого себя
    if user.id == current_user.id:
        flash('Нельзя удалить свой собственный аккаунт', 'error')
        return redirect(url_for('admin_users'))
    
    # Нельзя удалить последнего администратора
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Нельзя удалить последнего администратора', 'error')
            return redirect(url_for('admin_users'))
    
    username = user.username
    
    # Удаляем пользователя (каскадное удаление)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Пользователь {username} удален успешно', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/ssl/upload', methods=['POST'])
@admin_required
def upload_ssl_certificate():
    """Загрузка SSL сертификата"""
    try:
        if 'certificate' not in request.files or 'private_key' not in request.files:
            return jsonify({'success': False, 'message': 'Необходимо загрузить оба файла'})
        
        cert_file = request.files['certificate']
        key_file = request.files['private_key']
        
        if cert_file.filename == '' or key_file.filename == '':
            return jsonify({'success': False, 'message': 'Файлы не выбраны'})
        
        # Проверяем расширения
        if not cert_file.filename.endswith('.pem') and not cert_file.filename.endswith('.crt'):
            return jsonify({'success': False, 'message': 'Сертификат должен быть в формате .pem или .crt'})
        
        if not key_file.filename.endswith('.pem') and not key_file.filename.endswith('.key'):
            return jsonify({'success': False, 'message': 'Приватный ключ должен быть в формате .pem или .key'})
        
        # Создаем папку ssl если её нет
        ssl_dir = 'ssl'
        if not os.path.exists(ssl_dir):
            os.makedirs(ssl_dir)
            print(f"✅ Создана папка {ssl_dir}")
        
        # Сохраняем файлы
        cert_path = os.path.join(ssl_dir, 'cert.pem')
        key_path = os.path.join(ssl_dir, 'key.pem')
        
        print(f"💾 Сохранение сертификата в: {cert_path}")
        print(f"💾 Сохранение ключа в: {key_path}")
        
        cert_file.save(cert_path)
        key_file.save(key_path)
        
        # Устанавливаем правильные права доступа
        os.chmod(key_path, 0o600)
        os.chmod(cert_path, 0o644)
        
        print(f"✅ Файлы сохранены с правами:")
        print(f"   Сертификат: {oct(os.stat(cert_path).st_mode)[-3:]}")
        print(f"   Ключ: {oct(os.stat(key_path).st_mode)[-3:]}")
        
        flash('SSL сертификат успешно загружен! Перезапустите сервер для применения изменений.', 'success')
        return jsonify({'success': True, 'message': 'SSL сертификат загружен успешно'})
        
    except Exception as e:
        print(f"❌ Ошибка загрузки SSL: {e}")
        return jsonify({'success': False, 'message': f'Ошибка загрузки: {str(e)}'})

@app.route('/admin/ssl/generate', methods=['POST'])
@admin_required
def generate_self_signed_certificate():
    """Генерация самоподписанного сертификата"""
    try:
        from ssl_manager import SSLManager
        
        ssl_manager = SSLManager()
        result = ssl_manager.generate_self_signed()
        
        if result['success']:
            flash('Самоподписанный сертификат успешно создан! Перезапустите сервер для применения изменений.', 'success')
            return jsonify({'success': True, 'message': 'Сертификат создан успешно'})
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка генерации: {str(e)}'})

@app.route('/admin/ssl/letsencrypt', methods=['POST'])
@admin_required
def setup_lets_encrypt():
    """Настройка Let's Encrypt сертификата"""
    try:
        data = request.get_json()
        domain = data.get('domain')
        email = data.get('email')
        
        if not domain or not email:
            return jsonify({'success': False, 'message': 'Необходимо указать домен и email'})
        
        from ssl_manager import SSLManager
        
        ssl_manager = SSLManager()
        result = ssl_manager.setup_lets_encrypt(domain, email)
        
        if result['success']:
            flash('Let\'s Encrypt сертификат успешно настроен! Перезапустите сервер для применения изменений.', 'success')
            return jsonify({'success': True, 'message': 'Сертификат настроен успешно'})
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка настройки: {str(e)}'})

@app.route('/admin/ssl/text-upload', methods=['POST'])
@admin_required
def upload_ssl_text():
    """Загрузка SSL сертификата текстом"""
    try:
        data = request.get_json()
        certificate = data.get('certificate', '').strip()
        private_key = data.get('private_key', '').strip()
        
        if not certificate or not private_key:
            return jsonify({'success': False, 'message': 'Необходимо заполнить оба поля'})
        
        # Проверяем формат сертификата
        if not certificate.startswith('-----BEGIN CERTIFICATE-----') or not certificate.endswith('-----END CERTIFICATE-----'):
            return jsonify({'success': False, 'message': 'Неверный формат сертификата'})
        
        # Проверяем формат ключа
        if not (private_key.startswith('-----BEGIN PRIVATE KEY-----') or 
                private_key.startswith('-----BEGIN RSA PRIVATE KEY-----')) or not private_key.endswith('-----END PRIVATE KEY-----'):
            return jsonify({'success': False, 'message': 'Неверный формат приватного ключа'})
        
        # Используем новый SSL менеджер
        from simple_ssl import ssl_manager
        
        if ssl_manager.save_certificate(certificate, private_key):
            return jsonify({'success': True, 'message': 'SSL сертификат успешно сохранен! Перезапустите сервер для применения изменений.'})
        else:
            return jsonify({'success': False, 'message': 'Ошибка сохранения SSL файлов'})
        
    except Exception as e:
        print(f"❌ Ошибка сохранения SSL: {e}")
        return jsonify({'success': False, 'message': f'Ошибка сохранения: {str(e)}'})

@app.route('/surveys/create', methods=['GET', 'POST'])
@login_required
@survey_creation_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        is_anonymous = 'is_anonymous' in request.form
        require_auth = 'require_auth' in request.form
        require_name = 'require_name' in request.form
        
        survey = Survey(
            title=title,
            description=description,
            is_anonymous=is_anonymous,
            require_auth=require_auth,
            require_name=require_name,
            creator_id=current_user.id
        )
        db.session.add(survey)
        db.session.commit()
        
        # Добавляем вопросы
        questions_data = json.loads(request.form.get('questions', '[]'))
        for i, q_data in enumerate(questions_data):
            question = Question(
                text=q_data['text'],
                type=q_data['type'],
                options=json.dumps(q_data.get('options', [])),
                is_required=q_data.get('is_required', True),
                allow_other=q_data.get('allow_other', False),
                other_text=q_data.get('other_text', 'Другой вариант'),
                rating_min=q_data.get('rating_min', 1),
                rating_max=q_data.get('rating_max', 5),
                rating_labels=json.dumps(q_data.get('rating_labels', [])),
                grid_rows=json.dumps(q_data.get('grid_rows', [])),
                grid_columns=json.dumps(q_data.get('grid_columns', [])),
                question_order=i,
                survey_id=survey.id
            )
            db.session.add(question)
        
        db.session.commit()
        flash('Опрос создан успешно', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_survey.html')

@app.route('/surveys/<int:survey_id>')
def view_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    return render_template('view_survey.html', survey=survey)

@app.route('/surveys/<int:survey_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    # Проверяем права на редактирование
    if survey.creator_id != current_user.id:
        flash('У вас нет прав для редактирования этого опроса', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Обновляем основную информацию
        survey.title = request.form.get('title')
        survey.description = request.form.get('description')
        survey.is_anonymous = 'is_anonymous' in request.form
        survey.require_auth = 'require_auth' in request.form
        survey.require_name = 'require_name' in request.form
        
        # Удаляем старые вопросы
        Question.query.filter_by(survey_id=survey.id).delete()
        
        # Добавляем новые вопросы
        questions_data = json.loads(request.form.get('questions', '[]'))
        for i, q_data in enumerate(questions_data):
            question = Question(
                text=q_data['text'],
                type=q_data['type'],
                options=json.dumps(q_data.get('options', [])),
                is_required=q_data.get('is_required', True),
                allow_other=q_data.get('allow_other', False),
                other_text=q_data.get('other_text', 'Другой вариант'),
                rating_min=q_data.get('rating_min', 1),
                rating_max=q_data.get('rating_max', 5),
                rating_labels=json.dumps(q_data.get('rating_labels', [])),
                grid_rows=json.dumps(q_data.get('grid_rows', [])),
                grid_columns=json.dumps(q_data.get('grid_columns', [])),
                question_order=i,
                survey_id=survey.id
            )
            db.session.add(question)
        
        db.session.commit()
        flash('Опрос обновлен успешно', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_survey.html', survey=survey)

@app.route('/surveys/<int:survey_id>/submit', methods=['POST'])
def submit_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if survey.require_auth and not current_user.is_authenticated:
        flash('Для прохождения этого опроса требуется авторизация', 'error')
        return redirect(url_for('login'))
    
    # Получаем имя респондента, если требуется
    respondent_name = None
    if survey.require_name:
        respondent_name = request.form.get('respondent_name')
        if not respondent_name:
            flash('Пожалуйста, укажите ваше имя', 'error')
            return redirect(url_for('view_survey', survey_id=survey_id))
    
    # Создаем ответ на опрос
    response = SurveyResponse(
        survey_id=survey.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        respondent_name=respondent_name,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        completion_time=request.form.get('completion_time', type=int)  # Время в секундах
    )
    db.session.add(response)
    db.session.commit()
    
    # Сохраняем ответы на вопросы
    for question in survey.questions:
        answer_value = request.form.get(f'question_{question.id}')
        if answer_value:
            # Обрабатываем разные типы ответов
            if question.type == 'checkbox':
                # Для флажков ответ может быть списком
                if isinstance(answer_value, list):
                    answer_value = json.dumps(answer_value)
            
            answer = Answer(
                question_id=question.id,
                response_id=response.id,
                value=answer_value,
                is_other=request.form.get(f'question_{question.id}_other') == 'true'
            )
            db.session.add(answer)
    
    db.session.commit()
    flash('Опрос успешно пройден!', 'success')
    return redirect(url_for('index'))

@app.route('/surveys/<int:survey_id>/results')
@login_required
def survey_results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if not current_user.is_admin and survey.creator_id != current_user.id:
        flash('У вас нет доступа к результатам этого опроса', 'error')
        return redirect(url_for('dashboard'))
    
    # Получаем все ответы на опрос
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).order_by(SurveyResponse.created_at.desc()).all()
    
    # Анализ общих результатов
    results = {}
    for question in survey.questions:
        try:
            if question.type == 'multiple_choice':
                # Безопасно загружаем опции
                try:
                    if question.options and question.options.strip():
                        options = json.loads(question.options)
                        if isinstance(options, list) and options:
                            counts = {opt: 0 for opt in options}
                            for answer in question.answers:
                                if answer.value in counts:
                                    counts[answer.value] += 1
                            results[question.id] = {
                                'type': 'multiple_choice',
                                'text': question.text,
                                'data': counts
                            }
                        else:
                            # Если опции пустые или невалидные
                            results[question.id] = {
                                'type': 'multiple_choice',
                                'text': question.text,
                                'data': {},
                                'error': 'Варианты ответов не настроены'
                            }
                    else:
                        # Если опции отсутствуют
                        results[question.id] = {
                            'type': 'multiple_choice',
                            'text': question.text,
                            'data': {},
                            'error': 'Варианты ответов не настроены'
                        }
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"❌ Ошибка парсинга опций для вопроса {question.id}: {e}")
                    results[question.id] = {
                        'type': 'multiple_choice',
                        'text': question.text,
                        'data': {},
                        'error': 'Ошибка в настройке вариантов ответов'
                    }
                    
            elif question.type == 'rating':
                ratings = []
                for answer in question.answers:
                    try:
                        if answer.value and answer.value.isdigit():
                            ratings.append(int(answer.value))
                    except (ValueError, TypeError):
                        continue
                
                if ratings:
                    # Создаем данные для графика рейтингов
                    rating_data = {}
                    for rating in range(1, 11):
                        rating_data[rating] = ratings.count(rating)
                    
                    results[question.id] = {
                        'type': 'rating',
                        'text': question.text,
                        'average': sum(ratings) / len(ratings),
                        'count': len(ratings),
                        'data': rating_data
                    }
                else:
                    results[question.id] = {
                        'type': 'rating',
                        'text': question.text,
                        'average': 0,
                        'count': 0,
                        'data': {},
                        'error': 'Нет валидных ответов'
                    }
                    
            else:  # text
                answers = []
                for answer in question.answers:
                    if answer.value and answer.value.strip():
                        answers.append(answer.value.strip())
                
                results[question.id] = {
                    'type': 'text',
                    'text': question.text,
                    'answers': answers
                }
                
        except Exception as e:
            print(f"❌ Ошибка обработки вопроса {question.id}: {e}")
            results[question.id] = {
                'type': 'error',
                'text': question.text,
                'error': f'Ошибка обработки: {str(e)}'
            }
    
    return render_template('survey_results.html', survey=survey, results=results, responses=responses)

@app.route('/surveys/<int:survey_id>/export-excel')
@login_required
def export_survey_excel(survey_id):
    """Улучшенный экспорт результатов опроса в Excel с диаграммами и графиками"""
    try:
        import xlsxwriter
        from io import BytesIO
        from flask import send_file
        
        survey = Survey.query.get_or_404(survey_id)
        
        if not current_user.is_admin and survey.creator_id != current_user.id:
            flash('У вас нет доступа к результатам этого опроса', 'error')
            return redirect(url_for('dashboard'))
        
        # Создаем Excel файл в памяти
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Стили
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': 'white',
            'bg_color': '#DC3545',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#F8F9FA',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0'
        })
        
        # ========== ЛИСТ 1: ОБЗОР ОПРОСА ==========
        ws_overview = workbook.add_worksheet('Обзор опроса')
        
        # Заголовок
        ws_overview.merge_range('A1:F1', f'ОТЧЕТ ПО ОПРОСУ: {survey.title}', header_format)
        ws_overview.set_row(0, 30)
        
        # Информация об опросе
        row = 2
        info_data = [
            ("Название опроса:", survey.title),
            ("Описание:", survey.description or "Не указано"),
            ("Создатель:", survey.creator.username),
            ("Дата создания:", survey.created_at.strftime('%d.%m.%Y %H:%M')),
            ("Тип опроса:", get_survey_type_name(survey)),
            ("Всего ответов:", len(survey.responses)),
            ("Всего вопросов:", len(survey.questions))
        ]
        
        for label, value in info_data:
            ws_overview.write(f'A{row}', label, subheader_format)
            ws_overview.write(f'B{row}', str(value), data_format)
            row += 1
        
        # ========== ЛИСТ 2: ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ==========
        ws_results = workbook.add_worksheet('Детальные результаты')
        
        # Заголовки
        ws_results.write('A1', 'Вопрос', subheader_format)
        ws_results.write('B1', 'Тип', subheader_format)
        ws_results.write('C1', 'Всего ответов', subheader_format)
        ws_results.write('D1', 'Статистика', subheader_format)
        ws_results.write('E1', 'Анализ', subheader_format)
        
        row = 1
        for question in survey.questions:
            ws_results.write(f'A{row}', question.text, data_format)
            ws_results.write(f'B{row}', get_question_type_name(question.type), data_format)
            ws_results.write(f'C{row}', len(question.answers), number_format)
            ws_results.write(f'D{row}', get_question_statistics(question), data_format)
            ws_results.write(f'E{row}', get_question_analysis(question), data_format)
            row += 1
        
        # ========== ЛИСТ 3: ОТВЕТЫ РЕСПОНДЕНТОВ ==========
        ws_responses = workbook.add_worksheet('Ответы респондентов')
        
        # Заголовки
        col = 0
        ws_responses.write(0, col, 'ID ответа', subheader_format)
        col += 1
        ws_responses.write(0, col, 'Дата ответа', subheader_format)
        col += 1
        ws_responses.write(0, col, 'IP адрес', subheader_format)
        col += 1
        
        if survey.require_name:
            ws_responses.write(0, col, 'Имя респондента', subheader_format)
            col += 1
        
        for question in survey.questions:
            ws_responses.write(0, col, f'Q{question.question_order + 1}: {question.text[:30]}...', subheader_format)
            col += 1
        
        # Данные ответов
        row = 1
        for response in survey.responses:
            col = 0
            ws_responses.write(row, col, response.id, number_format)
            col += 1
            ws_responses.write(row, col, response.created_at.strftime('%d.%m.%Y %H:%M'), data_format)
            col += 1
            ws_responses.write(row, col, response.ip_address or 'Неизвестно', data_format)
            col += 1
            
            if survey.require_name:
                ws_responses.write(row, col, response.respondent_name or 'Не указано', data_format)
                col += 1
            
            for question in survey.questions:
                answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()
                answer_text = format_answer_for_excel(answer, question) if answer else 'Нет ответа'
                ws_responses.write(row, col, answer_text, data_format)
                col += 1
            
            row += 1
        
        # ========== ЛИСТ 4: АНАЛИТИКА С ДИАГРАММАМИ ==========
        ws_analytics = workbook.add_worksheet('Аналитика')
        
        # Заголовок
        ws_analytics.merge_range('A1:F1', 'АНАЛИТИКА ОПРОСА', header_format)
        ws_analytics.set_row(0, 30)
        
        # Создаем диаграммы для каждого вопроса
        chart_row = 3
        for question in survey.questions:
            if question.type in ['single_choice', 'multiple_choice', 'dropdown']:
                # Диаграмма для вопросов с вариантами ответов
                options = json.loads(question.options) if question.options else []
                if options:
                    # Подготавливаем данные для диаграммы
                    option_counts = {option: 0 for option in options}
                    for answer in question.answers:
                        if answer.value in option_counts:
                            option_counts[answer.value] += 1
                    
                    # Записываем данные
                    ws_analytics.write(f'A{chart_row}', f'Вопрос: {question.text}', subheader_format)
                    chart_row += 1
                    
                    data_row = chart_row
                    for option, count in option_counts.items():
                        ws_analytics.write(f'A{data_row}', option, data_format)
                        ws_analytics.write(f'B{data_row}', count, number_format)
                        data_row += 1
                    
                    # Создаем круговую диаграмму
                    chart = workbook.add_chart({'type': 'pie'})
                    chart.add_series({
                        'name': 'Распределение ответов',
                        'categories': [f'Аналитика', data_row - len(option_counts), 0, data_row - 1, 0],
                        'values': [f'Аналитика', data_row - len(option_counts), 1, data_row - 1, 1],
                    })
                    chart.set_title({'name': f'Распределение ответов: {question.text[:30]}...'})
                    chart.set_size({'width': 480, 'height': 300})
                    ws_analytics.insert_chart(f'D{chart_row}', chart)
                    
                    chart_row = data_row + 2
            
            elif question.type in ['rating', 'scale']:
                # Диаграмма для рейтинговых вопросов
                ratings = [int(answer.value) for answer in question.answers if answer.value and answer.value.isdigit()]
                if ratings:
                    # Подготавливаем данные для диаграммы
                    rating_counts = {}
                    min_rating = question.rating_min or 1
                    max_rating = question.rating_max or 10
                    
                    for rating in range(min_rating, max_rating + 1):
                        rating_counts[rating] = ratings.count(rating)
                    
                    # Записываем данные
                    ws_analytics.write(f'A{chart_row}', f'Вопрос: {question.text}', subheader_format)
                    chart_row += 1
                    
                    data_row = chart_row
                    for rating, count in rating_counts.items():
                        ws_analytics.write(f'A{data_row}', f'Оценка {rating}', data_format)
                        ws_analytics.write(f'B{data_row}', count, number_format)
                        data_row += 1
                    
                    # Создаем столбчатую диаграмму
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'Распределение оценок',
                        'categories': [f'Аналитика', data_row - len(rating_counts), 0, data_row - 1, 0],
                        'values': [f'Аналитика', data_row - len(rating_counts), 1, data_row - 1, 1],
                    })
                    chart.set_title({'name': f'Распределение оценок: {question.text[:30]}...'})
                    chart.set_x_axis({'name': 'Оценка'})
                    chart.set_y_axis({'name': 'Количество ответов'})
                    chart.set_size({'width': 480, 'height': 300})
                    ws_analytics.insert_chart(f'D{chart_row}', chart)
                    
                    chart_row = data_row + 2
        
        # Настройка ширины колонок
        for worksheet in [ws_overview, ws_results, ws_responses, ws_analytics]:
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 40)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:F', 20)
        
        # Закрываем workbook
        workbook.close()
        output.seek(0)
        
        # Отправляем файл
        filename = f"survey_{survey.id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Ошибка экспорта Excel: {e}")
        flash('Ошибка при создании Excel отчета', 'error')
        return redirect(url_for('survey_results', survey_id=survey_id))

@app.route('/surveys/<int:survey_id>/submit', methods=['POST'])
def submit_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if survey.require_auth and not current_user.is_authenticated:
        flash('Для прохождения этого опроса требуется авторизация', 'error')
        return redirect(url_for('login'))
    
    # Получаем имя респондента, если требуется
    respondent_name = None
    if survey.require_name:
        respondent_name = request.form.get('respondent_name')
        if not respondent_name:
            flash('Пожалуйста, укажите ваше имя', 'error')
            return redirect(url_for('view_survey', survey_id=survey_id))
    
    # Создаем ответ на опрос
    response = SurveyResponse(
        survey_id=survey.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        respondent_name=respondent_name,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        completion_time=request.form.get('completion_time', type=int)  # Время в секундах
    )
    db.session.add(response)
    db.session.commit()
    
    # Сохраняем ответы на вопросы
    for question in survey.questions:
        answer_value = request.form.get(f'question_{question.id}')
        if answer_value:
            # Обрабатываем разные типы ответов
            if question.type == 'checkbox':
                # Для флажков ответ может быть списком
                if isinstance(answer_value, list):
                    answer_value = json.dumps(answer_value)
            
            answer = Answer(
                question_id=question.id,
                response_id=response.id,
                value=answer_value,
                is_other=request.form.get(f'question_{question.id}_other') == 'true'
            )
            db.session.add(answer)
    
    db.session.commit()
    flash('Опрос успешно пройден!', 'success')
    return redirect(url_for('index'))

@app.route('/surveys/<int:survey_id>/results')
@login_required
def survey_results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if not current_user.is_admin and survey.creator_id != current_user.id:
        flash('У вас нет доступа к результатам этого опроса', 'error')
        return redirect(url_for('dashboard'))
    
    # Получаем все ответы на опрос
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).order_by(SurveyResponse.created_at.desc()).all()
    
    # Анализ общих результатов
    results = {}
    for question in survey.questions:
        try:
            if question.type == 'multiple_choice':
                # Безопасно загружаем опции
                try:
                    if question.options and question.options.strip():
                        options = json.loads(question.options)
                        if isinstance(options, list) and options:
                            counts = {opt: 0 for opt in options}
                            for answer in question.answers:
                                if answer.value in counts:
                                    counts[answer.value] += 1
                            
                            results[question.id] = {
                                'type': 'multiple_choice',
                                'text': question.text,
                                'options': options,
                                'counts': counts,
                                'total': len(question.answers)
                            }
                        else:
                            results[question.id] = {
                                'type': 'multiple_choice',
                                'text': question.text,
                                'error': 'Некорректные опции'
                            }
                    else:
                        results[question.id] = {
                            'type': 'multiple_choice',
                            'text': question.text,
                            'error': 'Опции не заданы'
                        }
                except json.JSONDecodeError:
                    results[question.id] = {
                        'type': 'multiple_choice',
                        'text': question.text,
                        'error': 'Ошибка парсинга опций'
                    }
    
    return render_template('survey_results.html', survey=survey, results=results, responses=responses)

@app.route('/surveys/<int:survey_id>/export-excel')
@login_required
def export_survey_excel(survey_id):
    """Улучшенный экспорт результатов опроса в Excel с диаграммами и графиками"""
    try:
        import xlsxwriter
        from io import BytesIO
        from flask import send_file
        
        survey = Survey.query.get_or_404(survey_id)
        
        if not current_user.is_admin and survey.creator_id != current_user.id:
            flash('У вас нет доступа к результатам этого опроса', 'error')
            return redirect(url_for('dashboard'))
        
        # Создаем Excel файл в памяти
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Стили
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': 'white',
            'bg_color': '#DC3545',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#F8F9FA',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': '0'
        })
        
        # ========== ЛИСТ 1: ОБЗОР ОПРОСА ==========
        ws_overview = workbook.add_worksheet('Обзор опроса')
        
        # Заголовок
        ws_overview.merge_range('A1:F1', f'ОТЧЕТ ПО ОПРОСУ: {survey.title}', header_format)
        ws_overview.set_row(0, 30)
        
        # Информация об опросе
        row = 2
        info_data = [
            ("Название опроса:", survey.title),
            ("Описание:", survey.description or "Не указано"),
            ("Создатель:", survey.creator.username),
            ("Дата создания:", survey.created_at.strftime('%d.%m.%Y %H:%M')),
            ("Тип опроса:", get_survey_type_name(survey)),
            ("Всего ответов:", len(survey.responses)),
            ("Всего вопросов:", len(survey.questions))
        ]
        
        for label, value in info_data:
            ws_overview.write(f'A{row}', label, subheader_format)
            ws_overview.write(f'B{row}', str(value), data_format)
            row += 1
        
        # ========== ЛИСТ 2: ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ==========
        ws_results = workbook.add_worksheet('Детальные результаты')
        
        # Заголовки
        ws_results.write('A1', 'Вопрос', subheader_format)
        ws_results.write('B1', 'Тип', subheader_format)
        ws_results.write('C1', 'Всего ответов', subheader_format)
        ws_results.write('D1', 'Статистика', subheader_format)
        ws_results.write('E1', 'Анализ', subheader_format)
        
        row = 1
        for question in survey.questions:
            ws_results.write(f'A{row}', question.text, data_format)
            ws_results.write(f'B{row}', get_question_type_name(question.type), data_format)
            ws_results.write(f'C{row}', len(question.answers), number_format)
            ws_results.write(f'D{row}', get_question_statistics(question), data_format)
            ws_results.write(f'E{row}', get_question_analysis(question), data_format)
            row += 1
        
        # ========== ЛИСТ 3: ОТВЕТЫ РЕСПОНДЕНТОВ ==========
        ws_responses = workbook.add_worksheet('Ответы респондентов')
        
        # Заголовки
        col = 0
        ws_responses.write(0, col, 'ID ответа', subheader_format)
        col += 1
        ws_responses.write(0, col, 'Дата ответа', subheader_format)
        col += 1
        ws_responses.write(0, col, 'IP адрес', subheader_format)
        col += 1
        
        if survey.require_name:
            ws_responses.write(0, col, 'Имя респондента', subheader_format)
            col += 1
        
        for question in survey.questions:
            ws_responses.write(0, col, f'Q{question.question_order + 1}: {question.text[:30]}...', subheader_format)
            col += 1
        
        # Данные ответов
        row = 1
        for response in survey.responses:
            col = 0
            ws_responses.write(row, col, response.id, number_format)
            col += 1
            ws_responses.write(row, col, response.created_at.strftime('%d.%m.%Y %H:%M'), data_format)
            col += 1
            ws_responses.write(row, col, response.ip_address or 'Неизвестно', data_format)
            col += 1
            
            if survey.require_name:
                ws_responses.write(row, col, response.respondent_name or 'Не указано', data_format)
                col += 1
            
            for question in survey.questions:
                answer = Answer.query.filter_by(response_id=response.id, question_id=question.id).first()
                answer_text = format_answer_for_excel(answer, question) if answer else 'Нет ответа'
                ws_responses.write(row, col, answer_text, data_format)
                col += 1
            
            row += 1
        
        # ========== ЛИСТ 4: АНАЛИТИКА С ДИАГРАММАМИ ==========
        ws_analytics = workbook.add_worksheet('Аналитика')
        
        # Заголовок
        ws_analytics.merge_range('A1:F1', 'АНАЛИТИКА ОПРОСА', header_format)
        ws_analytics.set_row(0, 30)
        
        # Создаем диаграммы для каждого вопроса
        chart_row = 3
        for question in survey.questions:
            if question.type in ['single_choice', 'multiple_choice', 'dropdown']:
                # Диаграмма для вопросов с вариантами ответов
                options = json.loads(question.options) if question.options else []
                if options:
                    # Подготавливаем данные для диаграммы
                    option_counts = {option: 0 for option in options}
                    for answer in question.answers:
                        if answer.value in option_counts:
                            option_counts[answer.value] += 1
                    
                    # Записываем данные
                    ws_analytics.write(f'A{chart_row}', f'Вопрос: {question.text}', subheader_format)
                    chart_row += 1
                    
                    data_row = chart_row
                    for option, count in option_counts.items():
                        ws_analytics.write(f'A{data_row}', option, data_format)
                        ws_analytics.write(f'B{data_row}', count, number_format)
                        data_row += 1
                    
                    # Создаем круговую диаграмму
                    chart = workbook.add_chart({'type': 'pie'})
                    chart.add_series({
                        'name': 'Распределение ответов',
                        'categories': [f'Аналитика', data_row - len(option_counts), 0, data_row - 1, 0],
                        'values': [f'Аналитика', data_row - len(option_counts), 1, data_row - 1, 1],
                    })
                    chart.set_title({'name': f'Распределение ответов: {question.text[:30]}...'})
                    chart.set_size({'width': 480, 'height': 300})
                    ws_analytics.insert_chart(f'D{chart_row}', chart)
                    
                    chart_row = data_row + 2
            
            elif question.type in ['rating', 'scale']:
                # Диаграмма для рейтинговых вопросов
                ratings = [int(answer.value) for answer in question.answers if answer.value and answer.value.isdigit()]
                if ratings:
                    # Подготавливаем данные для диаграммы
                    rating_counts = {}
                    min_rating = question.rating_min or 1
                    max_rating = question.rating_max or 10
                    
                    for rating in range(min_rating, max_rating + 1):
                        rating_counts[rating] = ratings.count(rating)
                    
                    # Записываем данные
                    ws_analytics.write(f'A{chart_row}', f'Вопрос: {question.text}', subheader_format)
                    chart_row += 1
                    
                    data_row = chart_row
                    for rating, count in rating_counts.items():
                        ws_analytics.write(f'A{data_row}', f'Оценка {rating}', data_format)
                        ws_analytics.write(f'B{data_row}', count, number_format)
                        data_row += 1
                    
                    # Создаем столбчатую диаграмму
                    chart = workbook.add_chart({'type': 'column'})
                    chart.add_series({
                        'name': 'Распределение оценок',
                        'categories': [f'Аналитика', data_row - len(rating_counts), 0, data_row - 1, 0],
                        'values': [f'Аналитика', data_row - len(rating_counts), 1, data_row - 1, 1],
                    })
                    chart.set_title({'name': f'Распределение оценок: {question.text[:30]}...'})
                    chart.set_x_axis({'name': 'Оценка'})
                    chart.set_y_axis({'name': 'Количество ответов'})
                    chart.set_size({'width': 480, 'height': 300})
                    ws_analytics.insert_chart(f'D{chart_row}', chart)
                    
                    chart_row = data_row + 2
        
        # Настройка ширины колонок
        for worksheet in [ws_overview, ws_results, ws_responses, ws_analytics]:
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 40)
            worksheet.set_column('E:E', 30)
            worksheet.set_column('F:F', 20)
        
        # Закрываем workbook
        workbook.close()
        output.seek(0)
        
        # Отправляем файл
        filename = f"survey_{survey.id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Ошибка экспорта в Excel: {e}")
        flash('Ошибка экспорта в Excel', 'error')
        return redirect(url_for('survey_results', survey_id=survey_id))

def get_survey_type_name(survey):
    """Получение названия типа опроса"""
    if survey.is_anonymous:
        return "Анонимный"
    elif survey.require_auth:
        return "С авторизацией"
    elif survey.require_name:
        return "С запросом имени"
    else:
        return "Обычный"

def get_question_type_name(question_type):
    """Получение названия типа вопроса"""
    type_names = {
        'text': 'Текст (строка)',
        'text_paragraph': 'Текст (Абзац)',
        'single_choice': 'Один из списка',
        'multiple_choice': 'Несколько из списка',
        'dropdown': 'Раскрывающийся список',
        'scale': 'Шкала',
        'rating': 'Оценка',
        'grid': 'Сетка',
        'checkbox_grid': 'Сетка из флажков',
        'date': 'Дата',
        'time': 'Время'
    }
    return type_names.get(question_type, question_type)

def get_question_options_text(question):
    """Получение текста вариантов ответов"""
    if question.type in ['single_choice', 'multiple_choice', 'dropdown']:
        try:
            options = json.loads(question.options) if question.options else []
            if options:
                options_text = '; '.join(options)
                if question.allow_other:
                    options_text += f"; {question.other_text or 'Другой вариант'}"
                return options_text
        except:
            pass
    elif question.type in ['rating', 'scale']:
        min_val = question.rating_min or 1
        max_val = question.rating_max or 10
        labels = question.rating_labels or []
        if labels and len(labels) >= 2:
            return f"От {min_val} до {max_val} ({labels[0]} - {labels[1]})"
        return f"От {min_val} до {max_val}"
    elif question.type in ['grid', 'checkbox_grid']:
        try:
            rows = json.loads(question.grid_rows) if question.grid_rows else []
            cols = json.loads(question.grid_columns) if question.grid_columns else []
            return f"Строки: {', '.join(rows)}; Столбцы: {', '.join(cols)}"
        except:
            pass
    return "Нет вариантов"

def get_question_statistics(question):
    """Получение статистики по вопросу"""
    answers = question.answers
    total_answers = len(answers)
    
    if question.type in ['single_choice', 'multiple_choice', 'dropdown']:
        try:
            options = json.loads(question.options) if question.options else []
            if options:
                counts = {opt: 0 for opt in options}
                other_count = 0
                
                for answer in answers:
                    if answer.is_other:
                        other_count += 1
                    elif answer.value in counts:
                        counts[answer.value] += 1
                
                stats_parts = [f"{opt}: {count}" for opt, count in counts.items()]
                if other_count > 0:
                    stats_parts.append(f"Другие: {other_count}")
                
                return f"Всего: {total_answers}; " + "; ".join(stats_parts)
        except:
            pass
    elif question.type in ['rating', 'scale']:
        ratings = [int(answer.value) for answer in answers if answer.value and answer.value.isdigit()]
        if ratings:
            avg = sum(ratings) / len(ratings)
            return f"Всего: {len(ratings)}; Средний: {avg:.2f}; Мин: {min(ratings)}; Макс: {max(ratings)}"
    elif question.type in ['text', 'text_paragraph']:
        if answers:
            avg_length = sum(len(answer.value) for answer in answers if answer.value) / len(answers)
            return f"Всего: {total_answers}; Средняя длина: {avg_length:.0f} символов"
    elif question.type in ['grid', 'checkbox_grid']:
        grid_count = 0
        for answer in answers:
            if '|' in answer.value:
                grid_count += 1
        return f"Всего: {total_answers}; Заполненных ячеек: {grid_count}"
    elif question.type in ['date', 'time']:
        return f"Всего: {total_answers}; Тип: {question.type}"
    
    return f"Всего ответов: {total_answers}"

def get_question_analysis(question):
    """Получение анализа вопроса"""
    answers = question.answers
    total_answers = len(answers)
    
    if total_answers == 0:
        return "Нет ответов"
    
    if question.type in ['rating', 'scale']:
        ratings = [int(answer.value) for answer in answers if answer.value and answer.value.isdigit()]
        if ratings:
            avg = sum(ratings) / len(ratings)
            max_rating = question.rating_max or 10
            if avg >= max_rating * 0.8:
                return "Высокие оценки"
            elif avg <= (question.rating_min or 1) * 1.2:
                return "Низкие оценки"
            else:
                return "Средние оценки"
    
    elif question.type in ['single_choice', 'multiple_choice', 'dropdown']:
        try:
            options = json.loads(question.options) if question.options else []
            if options:
                counts = {opt: 0 for opt in options}
                for answer in answers:
                    if answer.value in counts:
                        counts[answer.value] += 1
                
                max_option = max(counts.items(), key=lambda x: x[1])
                percentage = (max_option[1] / total_answers) * 100
                return f"Популярный ответ: {max_option[0]} ({percentage:.1f}%)"
        except:
            pass
    
    elif question.type == 'checkbox':
        try:
            options = json.loads(question.options) if question.options else []
            if options:
                counts = {opt: 0 for opt in options}
                for answer in answers:
                    if answer.value.startswith('['):
                        selected_options = json.loads(answer.value)
                        for opt in selected_options:
                            if opt in counts:
                                counts[opt] += 1
                    elif answer.value in counts:
                        counts[answer.value] += 1
                
                max_option = max(counts.items(), key=lambda x: x[1])
                percentage = (max_option[1] / total_answers) * 100
                return f"Популярный ответ: {max_option[0]} ({percentage:.1f}%)"
        except:
            pass
    
    elif question.type in ['text', 'text_paragraph']:
        if answers:
            avg_length = sum(len(answer.value) for answer in answers if answer.value) / len(answers)
            if avg_length > 100:
                return "Длинные ответы"
            elif avg_length < 20:
                return "Короткие ответы"
            else:
                return "Средние ответы"
    
    elif question.type in ['grid', 'checkbox_grid']:
        grid_count = 0
        for answer in answers:
            if '|' in answer.value:
                grid_count += 1
        if grid_count > total_answers * 0.8:
            return "Высокая заполняемость"
        elif grid_count < total_answers * 0.3:
            return "Низкая заполняемость"
        else:
            return "Средняя заполняемость"
    
    elif question.type in ['date', 'time']:
        return f"Всего ответов: {total_answers}"
    
    return "Анализ недоступен"

def format_answer_for_excel(answer, question):
    """Форматирование ответа для Excel"""
    if not answer or not answer.value:
        return "Нет ответа"
    
    if question.type == 'checkbox':
        try:
            # Для флажков ответ может быть JSON массивом
            if answer.value.startswith('['):
                selected_options = json.loads(answer.value)
                return '; '.join(selected_options)
        except:
            pass
    
    if question.type in ['grid', 'checkbox_grid']:
        if '|' in answer.value:
            row, col = answer.value.split('|', 1)
            return f"{row} → {col}"
    
    return str(answer.value)

@app.route('/surveys/<int:survey_id>/response/<int:response_id>')
@login_required
def view_response_detail(survey_id, response_id):
    """Просмотр детального ответа пользователя"""
    survey = Survey.query.get_or_404(survey_id)
    response = SurveyResponse.query.get_or_404(response_id)
    
    if not current_user.is_admin and survey.creator_id != current_user.id:
        flash('У вас нет доступа к результатам этого опроса', 'error')
        return redirect(url_for('dashboard'))
    
    if response.survey_id != survey_id:
        flash('Ответ не принадлежит указанному опросу', 'error')
        return redirect(url_for('survey_results', survey_id=survey_id))
    
    # Получаем ответы на вопросы
    answers = {}
    for answer in response.answers:
        question = answer.question
        if question:
            answers[question.id] = {
                'question_text': question.text,
                'question_type': question.type,
                'answer_value': answer.value,
                'question_options': question.options
            }
    
    return render_template('response_detail.html', 
                         survey=survey, 
                         response=response, 
                         answers=answers)

# LDAP маршруты
@app.route('/admin/ldap/test')
@admin_required
def test_ldap_connection():
    """Тестирование подключения к LDAP"""
    try:
        from ldap_manager import ldap_manager
        result = ldap_manager.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка: {str(e)}'})

@app.route('/admin/ldap/search')
@admin_required
def search_ldap_users():
    """Поиск пользователей в LDAP"""
    try:
        from ldap_manager import ldap_manager
        query = request.args.get('q', '')
        max_results = int(request.args.get('max', 50))
        
        users = ldap_manager.search_users(query, max_results)
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка: {str(e)}'})

@app.route('/admin/ldap/import', methods=['POST'])
@admin_required
def import_ldap_users():
    """Импорт пользователей из LDAP"""
    try:
        from ldap_manager import ldap_manager
        from werkzeug.security import generate_password_hash
        
        data = request.get_json()
        user_dns = data.get('user_dns', [])
        
        if not user_dns:
            return jsonify({'success': False, 'error': 'Не выбраны пользователи для импорта'})
        
        # Импортируем пользователей
        result = ldap_manager.import_users(user_dns)
        
        if result['success']:
            # Создаем пользователей в системе
            created_count = 0
            for user_data in result['imported_users']:
                # Проверяем, не существует ли уже пользователь
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    # Создаем нового пользователя
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'] or f"{user_data['username']}@buntergroup.com",
                        password_hash=generate_password_hash('changeme123'),  # Временный пароль
                        is_admin=False,
                        can_create_surveys=False
                    )
                    db.session.add(new_user)
                    created_count += 1
            
            if created_count > 0:
                db.session.commit()
                flash(f'Импортировано {created_count} пользователей из LDAP', 'success')
            else:
                flash('Все выбранные пользователи уже существуют в системе', 'info')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Ошибка импорта: {str(e)}'})

# ==================== РАСШИРЕННАЯ АНАЛИТИКА ====================

@app.route('/analytics')
@login_required
def analytics_dashboard():
    """Главная страница аналитики"""
    return render_template('analytics/dashboard.html')

@app.route('/analytics/survey/<int:survey_id>')
@login_required
def survey_analytics(survey_id):
    """Детальная аналитика по конкретному опросу"""
    survey = Survey.query.get_or_404(survey_id)
    
    # Проверяем права доступа
    if not current_user.is_admin and survey.creator_id != current_user.id:
        flash('У вас нет прав для просмотра аналитики этого опроса', 'error')
        return redirect(url_for('dashboard'))
    
    # Получаем аналитические данные
    analytics_data = get_survey_analytics(survey_id)
    
    return render_template('analytics/survey_analytics.html', 
                         survey=survey, 
                         analytics=analytics_data)

@app.route('/analytics/global')
@login_required
@admin_required
def global_analytics():
    """Глобальная аналитика по всем опросам"""
    analytics_data = get_global_analytics()
    return render_template('analytics/global_analytics.html', analytics=analytics_data)

@app.route('/analytics/user/<int:user_id>')
@login_required
@admin_required
def user_analytics(user_id):
    """Аналитика по конкретному пользователю"""
    user = User.query.get_or_404(user_id)
    analytics_data = get_user_analytics(user_id)
    return render_template('analytics/user_analytics.html', 
                         user=user, 
                         analytics=analytics_data)

@app.route('/analytics/cross-analysis')
@login_required
@admin_required
def cross_analysis():
    """Кросс-анализ между опросами"""
    analytics_data = get_cross_analysis()
    return render_template('analytics/cross_analysis.html', analytics=analytics_data)

@app.route('/api/analytics/survey/<int:survey_id>/chart-data')
@login_required
def get_survey_chart_data(survey_id):
    """API для получения данных для графиков опроса"""
    survey = Survey.query.get_or_404(survey_id)
    
    if not current_user.is_admin and survey.creator_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    chart_data = get_survey_chart_data_internal(survey_id)
    return jsonify(chart_data)

def get_survey_analytics(survey_id):
    """Получение аналитических данных по опросу"""
    survey = Survey.query.get(survey_id)
    if not survey:
        return None
    
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
    questions = Question.query.filter_by(survey_id=survey_id).order_by(Question.question_order).all()
    
    # Основные метрики
    total_responses = len(responses)
    completion_rate = 100.0  # Все начатые опросы считаются завершенными
    
    # Время прохождения
    completion_times = [r.completion_time for r in responses if r.completion_time]
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Анализ по вопросам
    question_analytics = []
    for question in questions:
        q_analytics = analyze_question(question, responses)
        # Преобразуем объект Question в словарь для JSON сериализации
        q_analytics['question'] = {
            'id': question.id,
            'text': question.text,
            'type': question.type,
            'is_required': question.is_required,
            'options': question.options,
            'allow_other': question.allow_other,
            'other_text': question.other_text,
            'rating_min': question.rating_min,
            'rating_max': question.rating_max,
            'rating_labels': question.rating_labels,
            'grid_rows': question.grid_rows,
            'grid_columns': question.grid_columns
        }
        question_analytics.append(q_analytics)
    
    # Временная аналитика
    time_analytics = get_time_analytics(responses)
    
    # Географическая аналитика (по IP)
    geo_analytics = get_geo_analytics(responses)
    
    return {
        'survey': survey,
        'total_responses': total_responses,
        'completion_rate': completion_rate,
        'avg_completion_time': avg_completion_time,
        'question_analytics': question_analytics,
        'time_analytics': time_analytics,
        'geo_analytics': geo_analytics
    }

def analyze_question(question, responses):
    """Анализ конкретного вопроса"""
    answers = Answer.query.filter_by(question_id=question.id).all()
    
    analytics = {
        'question': question,
        'total_answers': len(answers),
        'response_rate': 0,
        'data': {}
    }
    
    if question.type in ['single_choice', 'multiple_choice', 'dropdown']:
        options = json.loads(question.options) if question.options else []
        option_counts = {option: 0 for option in options}
        
        for answer in answers:
            if answer.value in option_counts:
                option_counts[answer.value] += 1
            elif answer.is_other:
                if 'Другие' not in option_counts:
                    option_counts['Другие'] = 0
                option_counts['Другие'] += 1
        
        analytics['data'] = option_counts
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type == 'checkbox':
        options = json.loads(question.options) if question.options else []
        option_counts = {option: 0 for option in options}
        
        for answer in answers:
            selected_options = json.loads(answer.value) if answer.value.startswith('[') else [answer.value]
            for option in selected_options:
                if option in option_counts:
                    option_counts[option] += 1
                elif answer.is_other:
                    if 'Другие' not in option_counts:
                        option_counts['Другие'] = 0
                    option_counts['Другие'] += 1
        
        analytics['data'] = option_counts
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type in ['rating', 'scale']:
        ratings = [int(answer.value) for answer in answers if answer.value.isdigit()]
        if ratings:
            analytics['data'] = {
                'min': min(ratings),
                'max': max(ratings),
                'avg': sum(ratings) / len(ratings),
                'distribution': {str(i): ratings.count(i) for i in range(question.rating_min or 1, (question.rating_max or 10) + 1)}
            }
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type in ['text', 'text_paragraph']:
        text_answers = [answer.value for answer in answers if answer.value]
        avg_length = sum(len(text) for text in text_answers) / len(text_answers) if text_answers else 0
        analytics['data'] = {
            'total_texts': len(text_answers),
            'avg_length': avg_length,
            'answers': text_answers
        }
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type in ['grid', 'checkbox_grid']:
        grid_data = {}
        for answer in answers:
            if '|' in answer.value:
                row, col = answer.value.split('|', 1)
                key = f"{row}|{col}"
                if key in grid_data:
                    grid_data[key] += 1
                else:
                    grid_data[key] = 1
        
        analytics['data'] = grid_data
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type in ['date', 'time']:
        date_time_answers = [answer.value for answer in answers if answer.value]
        analytics['data'] = date_time_answers
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
        
    elif question.type == 'text':
        text_answers = [answer.value for answer in answers]
        analytics['data'] = {
            'total_texts': len(text_answers),
            'avg_length': sum(len(text) for text in text_answers) / len(text_answers) if text_answers else 0,
            'sample_answers': text_answers[:5]  # Первые 5 ответов для примера
        }
        analytics['response_rate'] = (len(answers) / len(responses)) * 100 if responses else 0
    
    return analytics

def get_time_analytics(responses):
    """Анализ по времени"""
    if not responses:
        return {}
    
    # Группировка по дням
    daily_responses = {}
    for response in responses:
        date_key = response.created_at.strftime('%Y-%m-%d')
        daily_responses[date_key] = daily_responses.get(date_key, 0) + 1
    
    # Группировка по часам
    hourly_responses = {}
    for response in responses:
        hour_key = response.created_at.hour
        hourly_responses[hour_key] = hourly_responses.get(hour_key, 0) + 1
    
    return {
        'daily': daily_responses,
        'hourly': hourly_responses,
        'peak_hour': max(hourly_responses.items(), key=lambda x: x[1])[0] if hourly_responses else 0
    }

def get_geo_analytics(responses):
    """Географическая аналитика (упрощенная по IP)"""
    if not responses:
        return {}
    
    # Группировка по IP (упрощенная геолокация)
    ip_groups = {}
    for response in responses:
        # Упрощенная группировка по первым трем октетам IP
        ip_parts = response.ip_address.split('.')
        if len(ip_parts) >= 3:
            ip_group = '.'.join(ip_parts[:3]) + '.x'
            ip_groups[ip_group] = ip_groups.get(ip_group, 0) + 1
    
    return {
        'ip_groups': ip_groups,
        'unique_ips': len(set(r.ip_address for r in responses))
    }

def get_global_analytics():
    """Глобальная аналитика по всем опросам"""
    surveys = Survey.query.all()
    users = User.query.all()
    all_responses = SurveyResponse.query.all()
    
    # Общая статистика
    total_surveys = len(surveys)
    total_users = len(users)
    total_responses = len(all_responses)
    
    # Активные опросы (с ответами)
    active_surveys = len([s for s in surveys if len(s.responses) > 0])
    
    # Топ опросы по количеству ответов
    top_surveys = sorted(surveys, key=lambda x: len(x.responses), reverse=True)[:10]
    
    # Статистика по пользователям
    user_stats = {
        'total': total_users,
        'admins': len([u for u in users if u.is_admin]),
        'survey_creators': len([u for u in users if u.can_create_surveys]),
        'active_respondents': len(set(r.user_id for r in all_responses if r.user_id))
    }
    
    # Временная статистика
    time_stats = get_time_analytics(all_responses)
    
    return {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'total_responses': total_responses,
        'user_stats': user_stats,
        'top_surveys': top_surveys,
        'time_stats': time_stats
    }

def get_user_analytics(user_id):
    """Аналитика по пользователю"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Опросы пользователя
    user_surveys = Survey.query.filter_by(creator_id=user_id).all()
    
    # Ответы пользователя
    user_responses = SurveyResponse.query.filter_by(user_id=user_id).all()
    
    # Статистика
    total_surveys_created = len(user_surveys)
    total_responses_given = len(user_responses)
    
    # Активность по времени
    activity_stats = get_time_analytics(user_responses)
    
    return {
        'user': user,
        'surveys_created': user_surveys,
        'responses_given': user_responses,
        'total_surveys_created': total_surveys_created,
        'total_responses_given': total_responses_given,
        'activity_stats': activity_stats
    }

def get_cross_analysis():
    """Кросс-анализ между опросами"""
    surveys = Survey.query.all()
    
    # Корреляции между опросами
    correlations = []
    
    # Анализ популярности типов вопросов
    question_types = {}
    for survey in surveys:
        for question in survey.questions:
            question_types[question.type] = question_types.get(question.type, 0) + 1
    
    # Анализ эффективности типов опросов
    survey_type_effectiveness = {
        'anonymous': {'total': 0, 'responses': 0},
        'auth_required': {'total': 0, 'responses': 0},
        'name_required': {'total': 0, 'responses': 0}
    }
    
    for survey in surveys:
        if survey.is_anonymous:
            survey_type_effectiveness['anonymous']['total'] += 1
            survey_type_effectiveness['anonymous']['responses'] += len(survey.responses)
        if survey.require_auth:
            survey_type_effectiveness['auth_required']['total'] += 1
            survey_type_effectiveness['auth_required']['responses'] += len(survey.responses)
        if survey.require_name:
            survey_type_effectiveness['name_required']['total'] += 1
            survey_type_effectiveness['name_required']['responses'] += len(survey.responses)
    
    return {
        'question_types': question_types,
        'survey_type_effectiveness': survey_type_effectiveness,
        'correlations': correlations
    }

def get_survey_chart_data_internal(survey_id):
    """Внутренняя функция для получения данных графиков"""
    survey = Survey.query.get(survey_id)
    if not survey:
        return {}
    
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
    questions = Question.query.filter_by(survey_id=survey_id).order_by(Question.question_order).all()
    
    chart_data = {
        'response_timeline': [],
        'question_charts': []
    }
    
    # Временная линия ответов
    daily_counts = {}
    for response in responses:
        date_key = response.created_at.strftime('%Y-%m-%d')
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    chart_data['response_timeline'] = [
        {'date': date, 'count': count} 
        for date, count in sorted(daily_counts.items())
    ]
    
    # Данные для графиков вопросов
    for question in questions:
        q_data = analyze_question(question, responses)
        chart_data['question_charts'].append({
            'question_id': question.id,
            'question_text': question.text,
            'type': question.type,
            'data': q_data['data'],
            'total_answers': q_data['total_answers'],
            'response_rate': q_data['response_rate']
        })
    
    return chart_data

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Проверяем SSL и запускаем соответственно
    try:
        from simple_ssl import ssl_manager
        
        print("🔍 Проверка SSL конфигурации...")
        
        if ssl_manager.is_ssl_ready():
            print("✅ SSL статус: Включен")
            ssl_context = ssl_manager.get_ssl_context()
            
            if ssl_context:
                print("🔒 Запуск с SSL сертификатом...")
                print(f"   Порт: 5000 (HTTPS)")
                print(f"   Сертификат: {ssl_manager.cert_file}")
                print(f"   Ключ: {ssl_manager.key_file}")
                
                app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=ssl_context)
            else:
                print("⚠️  SSL файлы найдены, но не валидны. Запуск без SSL...")
                print("   Проверьте права доступа и формат файлов")
                app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("🌐 Запуск без SSL...")
            print("   Проверьте наличие файлов cert.pem и key.pem в папке ssl/")
            app.run(debug=True, host='0.0.0.0', port=5000)
            
    except ImportError as e:
        print(f"⚠️  SSL менеджер недоступен: {e}")
        print("   Запуск без SSL...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Ошибка SSL конфигурации: {e}")
        print("   Запуск без SSL...")
        app.run(debug=True, host='0.0.0.0', port=5000)