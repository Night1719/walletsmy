import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class Survey(models.Model):
    """Модель опроса"""
    
    SURVEY_TYPE_CHOICES = [
        ('anonymous', 'Анонимный'),
        ('authenticated', 'С авторизацией'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активный'),
        ('paused', 'Приостановлен'),
        ('closed', 'Закрыт'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_surveys',
        verbose_name='Создатель'
    )
    
    survey_type = models.CharField(
        max_length=20,
        choices=SURVEY_TYPE_CHOICES,
        default='authenticated',
        verbose_name='Тип опроса'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичный'
    )
    
    login_required = models.BooleanField(
        default=True,
        verbose_name='Требуется авторизация'
    )
    
    allow_multiple_responses = models.BooleanField(
        default=False,
        verbose_name='Разрешить множественные ответы'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата начала'
    )
    
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата окончания'
    )
    
    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        """Проверяет, активен ли опрос"""
        now = timezone.now()
        if self.status != 'active':
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    @property
    def total_responses(self):
        """Общее количество ответов"""
        return self.responses.count()
    
    @property
    def completion_rate(self):
        """Процент завершения опроса"""
        if not self.questions.exists():
            return 0
        total_questions = self.questions.count()
        completed_responses = self.responses.filter(is_completed=True).count()
        if total_questions == 0:
            return 0
        return round((completed_responses / total_questions) * 100, 2)


class Question(models.Model):
    """Модель вопроса"""
    
    QUESTION_TYPE_CHOICES = [
        ('text', 'Текстовый ответ'),
        ('textarea', 'Многострочный текст'),
        ('choice', 'Выбор одного варианта'),
        ('multiple_choice', 'Выбор нескольких вариантов'),
        ('scale', 'Шкала'),
        ('date', 'Дата'),
        ('time', 'Время'),
        ('email', 'Email'),
        ('phone', 'Телефон'),
    ]
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Опрос'
    )
    
    text = models.TextField(
        verbose_name='Текст вопроса'
    )
    
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name='Тип вопроса'
    )
    
    is_required = models.BooleanField(
        default=True,
        verbose_name='Обязательный'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    
    help_text = models.TextField(
        blank=True,
        verbose_name='Подсказка'
    )
    
    min_choices = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Минимум вариантов'
    )
    
    max_choices = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Максимум вариантов'
    )
    
    min_value = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Минимальное значение'
    )
    
    max_value = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Максимальное значение'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.survey.title} - {self.text[:50]}"


class QuestionChoice(models.Model):
    """Модель варианта ответа для вопроса"""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Вопрос'
    )
    
    text = models.CharField(
        max_length=200,
        verbose_name='Текст варианта'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    
    value = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Значение'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


class SurveyResponse(models.Model):
    """Модель ответа на опрос"""
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Опрос'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name='Пользователь'
    )
    
    anonymous_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Анонимный ID'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name='Завершен'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время начала'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Время завершения'
    )
    
    class Meta:
        verbose_name = 'Ответ на опрос'
        verbose_name_plural = 'Ответы на опросы'
        ordering = ['-started_at']
    
    def __str__(self):
        if self.user:
            return f"{self.survey.title} - {self.user.username}"
        return f"{self.survey.title} - Анонимный ({self.anonymous_id})"


class Answer(models.Model):
    """Модель ответа на конкретный вопрос"""
    
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Ответ на опрос'
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Вопрос'
    )
    
    text_answer = models.TextField(
        blank=True,
        verbose_name='Текстовый ответ'
    )
    
    selected_choices = models.ManyToManyField(
        QuestionChoice,
        blank=True,
        verbose_name='Выбранные варианты'
    )
    
    numeric_answer = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Числовой ответ'
    )
    
    date_answer = models.DateField(
        blank=True,
        null=True,
        verbose_name='Ответ-дата'
    )
    
    time_answer = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Ответ-время'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.response} - {self.question.text[:30]}"