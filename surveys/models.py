from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Survey(models.Model):
    """Модель опроса"""
    
    class SurveyType(models.TextChoices):
        ANONYMOUS = 'anonymous', _('Анонимный')
        AUTHENTICATED = 'authenticated', _('С авторизацией')
    
    class SurveyStatus(models.TextChoices):
        DRAFT = 'draft', _('Черновик')
        ACTIVE = 'active', _('Активный')
        PAUSED = 'paused', _('Приостановлен')
        CLOSED = 'closed', _('Закрыт')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_surveys',
        verbose_name=_('Создатель')
    )
    
    survey_type = models.CharField(
        max_length=20,
        choices=SurveyType.choices,
        default=SurveyType.AUTHENTICATED,
        verbose_name=_('Тип опроса')
    )
    
    status = models.CharField(
        max_length=20,
        choices=SurveyStatus.choices,
        default=SurveyStatus.DRAFT,
        verbose_name=_('Статус')
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('Публичный')
    )
    
    requires_login = models.BooleanField(
        default=True,
        verbose_name=_('Требует авторизации')
    )
    
    allow_multiple_responses = models.BooleanField(
        default=False,
        verbose_name=_('Разрешить множественные ответы')
    )
    
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата начала')
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата окончания')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Опрос')
        verbose_name_plural = _('Опросы')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_active(self):
        """Проверяет, активен ли опрос"""
        if self.status != self.SurveyStatus.ACTIVE:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    @property
    def total_responses(self):
        """Общее количество ответов на опрос"""
        return self.responses.count()
    
    @property
    def completion_rate(self):
        """Процент завершения опроса"""
        if not self.questions.exists():
            return 0
        
        total_questions = self.questions.count()
        completed_responses = self.responses.filter(is_completed=True).count()
        
        if completed_responses == 0:
            return 0
        
        return round((completed_responses / total_questions) * 100, 2)


class Question(models.Model):
    """Модель вопроса"""
    
    class QuestionType(models.TextChoices):
        TEXT = 'text', _('Текстовый ответ')
        TEXTAREA = 'textarea', _('Многострочный текст')
        SINGLE_CHOICE = 'single_choice', _('Один выбор')
        MULTIPLE_CHOICE = 'multiple_choice', _('Множественный выбор')
        RATING = 'rating', _('Рейтинг')
        SCALE = 'scale', _('Шкала')
        DATE = 'date', _('Дата')
        TIME = 'time', _('Время')
        DATETIME = 'datetime', _('Дата и время')
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Опрос')
    )
    
    text = models.TextField(verbose_name=_('Текст вопроса'))
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        verbose_name=_('Тип вопроса')
    )
    
    is_required = models.BooleanField(
        default=True,
        verbose_name=_('Обязательный')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )
    
    help_text = models.TextField(
        blank=True,
        verbose_name=_('Подсказка')
    )
    
    # Для вопросов с выбором
    min_choices = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Минимум выборов')
    )
    
    max_choices = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Максимум выборов')
    )
    
    # Для рейтингов и шкал
    min_value = models.IntegerField(
        default=1,
        verbose_name=_('Минимальное значение')
    )
    
    max_value = models.IntegerField(
        default=5,
        verbose_name=_('Максимальное значение')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Вопрос')
        verbose_name_plural = _('Вопросы')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.survey.title} - {self.text[:50]}"


class QuestionChoice(models.Model):
    """Варианты ответов для вопросов с выбором"""
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name=_('Вопрос')
    )
    
    text = models.CharField(max_length=200, verbose_name=_('Текст варианта'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    
    class Meta:
        verbose_name = _('Вариант ответа')
        verbose_name_plural = _('Варианты ответов')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text}"


class SurveyResponse(models.Model):
    """Ответ на опрос"""
    
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Опрос')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name=_('Пользователь')
    )
    
    # Для анонимных опросов
    anonymous_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Анонимный ID')
    )
    
    # IP адрес для отслеживания
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP адрес')
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_('Завершен')
    )
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Начало заполнения'))
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Завершение заполнения')
    )
    
    class Meta:
        verbose_name = _('Ответ на опрос')
        verbose_name_plural = _('Ответы на опросы')
        ordering = ['-started_at']
    
    def __str__(self):
        if self.user:
            return f"{self.survey.title} - {self.user.username}"
        else:
            return f"{self.survey.title} - Анонимный ({self.anonymous_id})"
    
    def save(self, *args, **kwargs):
        if not self.anonymous_id and not self.user:
            import secrets
            self.anonymous_id = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)


class Answer(models.Model):
    """Ответ на конкретный вопрос"""
    
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Ответ на опрос')
    )
    
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_('Вопрос')
    )
    
    # Текстовые ответы
    text_answer = models.TextField(
        blank=True,
        verbose_name=_('Текстовый ответ')
    )
    
    # Выбранные варианты
    selected_choices = models.ManyToManyField(
        QuestionChoice,
        blank=True,
        verbose_name=_('Выбранные варианты')
    )
    
    # Числовые ответы (рейтинги, шкалы)
    numeric_answer = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Числовой ответ')
    )
    
    # Дата/время
    date_answer = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Ответ - дата')
    )
    
    time_answer = models.TimeField(
        null=True,
        blank=True,
        verbose_name=_('Ответ - время')
    )
    
    datetime_answer = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Ответ - дата и время')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Ответ')
        verbose_name_plural = _('Ответы')
        unique_together = ['response', 'question']
    
    def __str__(self):
        return f"{self.response} - {self.question.text[:30]}"
    
    def get_answer_display(self):
        """Возвращает отображаемое значение ответа"""
        if self.text_answer:
            return self.text_answer
        elif self.selected_choices.exists():
            return ', '.join([choice.text for choice in self.selected_choices.all()])
        elif self.numeric_answer is not None:
            return str(self.numeric_answer)
        elif self.date_answer:
            return self.date_answer.strftime('%d.%m.%Y')
        elif self.time_answer:
            return self.time_answer.strftime('%H:%M')
        elif self.datetime_answer:
            return self.datetime_answer.strftime('%d.%m.%Y %H:%M')
        return ''