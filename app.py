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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    questions = db.relationship('Question', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # text, multiple_choice, rating
    options = db.Column(db.Text)  # JSON для вариантов ответов
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    answers = db.relationship('Answer', backref='response', lazy=True, cascade='all, delete-orphan')

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_response.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Вспомогательные функции для шаблонов
@app.context_processor
def utility_processor():
    def from_json(json_string):
        """Преобразует JSON строку в Python объект"""
        try:
            if json_string:
                return json.loads(json_string)
            return []
        except (json.JSONDecodeError, TypeError):
            return []
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
    
    return {
        'count_responses': count_responses,
        'count_active_surveys': count_active_surveys,
        'format_date': format_date,
        'from_json': from_json
    }

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
    
    # SSL статус (заглушка для демонстрации)
    ssl_status = {
        'enabled': False,
        'certificate': None
    }
    
    # Проверяем наличие SSL файлов
    try:
        if os.path.exists('ssl/cert.pem') and os.path.exists('ssl/key.pem'):
            ssl_status['enabled'] = True
            # Здесь можно добавить парсинг сертификата
            ssl_status['certificate'] = {
                'subject': 'SSL Certificate',
                'expires': '2025-12-31'
            }
    except:
        pass
    
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

@app.route('/surveys/create', methods=['GET', 'POST'])
@login_required
@survey_creation_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        is_anonymous = 'is_anonymous' in request.form
        require_auth = 'require_auth' in request.form
        
        survey = Survey(
            title=title,
            description=description,
            is_anonymous=is_anonymous,
            require_auth=require_auth,
            creator_id=current_user.id
        )
        db.session.add(survey)
        db.session.commit()
        
        # Добавляем вопросы
        questions_data = json.loads(request.form.get('questions', '[]'))
        for q_data in questions_data:
            question = Question(
                text=q_data['text'],
                type=q_data['type'],
                options=json.dumps(q_data.get('options', [])),
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

@app.route('/surveys/<int:survey_id>/submit', methods=['POST'])
def submit_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if survey.require_auth and not current_user.is_authenticated:
        flash('Для прохождения этого опроса требуется авторизация', 'error')
        return redirect(url_for('login'))
    
    # Создаем ответ на опрос
    response = SurveyResponse(
        survey_id=survey.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        ip_address=request.remote_addr
    )
    db.session.add(response)
    db.session.commit()
    
    # Сохраняем ответы на вопросы
    for question in survey.questions:
        answer_value = request.form.get(f'question_{question.id}')
        if answer_value:
            answer = Answer(
                question_id=question.id,
                response_id=response.id,
                value=answer_value
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
    
    # Анализ результатов
    results = {}
    for question in survey.questions:
        if question.type == 'multiple_choice':
            options = json.loads(question.options)
            counts = {opt: 0 for opt in options}
            for answer in question.answers:
                if answer.value in counts:
                    counts[answer.value] += 1
            results[question.id] = {
                'type': 'multiple_choice',
                'text': question.text,
                'data': counts
            }
        elif question.type == 'rating':
            ratings = [int(answer.value) for answer in question.answers if answer.value.isdigit()]
            if ratings:
                results[question.id] = {
                    'type': 'rating',
                    'text': question.text,
                    'average': sum(ratings) / len(ratings),
                    'count': len(ratings)
                }
        else:  # text
            results[question.id] = {
                'type': 'text',
                'text': question.text,
                'answers': [answer.value for answer in question.answers]
            }
    
    return render_template('survey_results.html', survey=survey, results=results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)