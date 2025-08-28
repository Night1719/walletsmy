from django.contrib import admin
from django.utils.html import format_html
from .models import Survey, Question, QuestionChoice, SurveyResponse, Answer


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 1
    fields = ('text', 'order', 'value')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'is_required', 'order', 'help_text')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'text_answer', 'selected_choices', 'numeric_answer', 'date_answer', 'time_answer')
    can_delete = False


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'creator', 'survey_type', 'status', 'is_public',
        'total_responses_display', 'completion_rate_display', 'created_at'
    )
    
    list_filter = (
        'survey_type', 'status', 'is_public', 'login_required',
        'allow_multiple_responses', 'created_at', 'start_date', 'end_date'
    )
    
    search_fields = ('title', 'description', 'creator__username', 'creator__first_name', 'creator__last_name')
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_responses_display', 'completion_rate_display')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'creator')
        }),
        ('Настройки', {
            'fields': ('survey_type', 'status', 'is_public', 'login_required', 'allow_multiple_responses')
        }),
        ('Временные рамки', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    actions = ['activate_surveys', 'pause_surveys', 'close_surveys', 'make_public', 'make_private']
    
    def total_responses_display(self, obj):
        """Отображение общего количества ответов"""
        count = obj.total_responses
        if count == 0:
            return format_html('<span style="color: gray;">0</span>')
        elif count < 10:
            return format_html('<span style="color: orange;">{}</span>', count)
        else:
            return format_html('<span style="color: green;">{}</span>', count)
    total_responses_display.short_description = 'Ответов'
    
    def completion_rate_display(self, obj):
        """Отображение процента завершения"""
        rate = obj.completion_rate
        if rate == 0:
            return format_html('<span style="color: gray;">0%</span>')
        elif rate < 50:
            return format_html('<span style="color: red;">{}%</span>', rate)
        elif rate < 80:
            return format_html('<span style="color: orange;">{}%</span>', rate)
        else:
            return format_html('<span style="color: green;">{}%</span>', rate)
    completion_rate_display.short_description = 'Завершение'
    
    def activate_surveys(self, request, queryset):
        """Активировать опросы"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} опросов активировано.')
    activate_surveys.short_description = "Активировать опросы"
    
    def pause_surveys(self, request, queryset):
        """Приостановить опросы"""
        updated = queryset.update(status='paused')
        self.message_user(request, f'{updated} опросов приостановлено.')
    pause_surveys.short_description = "Приостановить опросы"
    
    def close_surveys(self, request, queryset):
        """Закрыть опросы"""
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} опросов закрыто.')
    close_surveys.short_description = "Закрыть опросы"
    
    def make_public(self, request, queryset):
        """Сделать опросы публичными"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} опросов сделано публичными.')
    make_public.short_description = "Сделать публичными"
    
    def make_private(self, request, queryset):
        """Сделать опросы приватными"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} опросов сделано приватными.')
    make_private.short_description = "Сделать приватными"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'is_required', 'order', 'created_at')
    list_filter = ('question_type', 'is_required', 'survey__status', 'created_at')
    search_fields = ('text', 'survey__title', 'help_text')
    ordering = ('survey', 'order', 'created_at')
    
    inlines = [QuestionChoiceInline]
    
    fieldsets = (
        (None, {
            'fields': ('survey', 'text', 'question_type', 'is_required', 'order', 'help_text')
        }),
        ('Настройки вариантов', {
            'fields': ('min_choices', 'max_choices'),
            'classes': ('collapse',)
        }),
        ('Настройки шкалы', {
            'fields': ('min_value', 'max_value'),
            'classes': ('collapse',)
        }),
        ('Система', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'order', 'value', 'created_at')
    list_filter = ('question__question_type', 'created_at')
    search_fields = ('text', 'question__text', 'value')
    ordering = ('question', 'order', 'created_at')
    
    fieldsets = (
        (None, {
            'fields': ('question', 'text', 'order', 'value')
        }),
        ('Система', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'user_display', 'ip_address', 'is_completed', 'started_at', 'completed_at')
    list_filter = ('is_completed', 'survey__status', 'started_at', 'completed_at')
    search_fields = ('survey__title', 'user__username', 'anonymous_id', 'ip_address')
    readonly_fields = ('started_at', 'completed_at')
    
    inlines = [AnswerInline]
    
    fieldsets = (
        (None, {
            'fields': ('survey', 'user', 'anonymous_id')
        }),
        ('Техническая информация', {
            'fields': ('ip_address', 'user_agent', 'is_completed')
        }),
        ('Временные метки', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """Отображение пользователя или анонимного ID"""
        if obj.user:
            return f"{obj.user.username} ({obj.user.get_full_name()})"
        return f"Анонимный ({obj.anonymous_id})"
    user_display.short_description = 'Пользователь'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'answer_display', 'created_at')
    list_filter = ('question__question_type', 'created_at')
    search_fields = ('response__survey__title', 'question__text', 'text_answer')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('response', 'question')
        }),
        ('Ответы', {
            'fields': ('text_answer', 'selected_choices', 'numeric_answer', 'date_answer', 'time_answer')
        }),
        ('Система', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def answer_display(self, obj):
        """Отображение ответа"""
        if obj.text_answer:
            return obj.text_answer[:50]
        elif obj.selected_choices.exists():
            choices = [choice.text for choice in obj.selected_choices.all()[:3]]
            return ', '.join(choices) + ('...' if obj.selected_choices.count() > 3 else '')
        elif obj.numeric_answer is not None:
            return str(obj.numeric_answer)
        elif obj.date_answer:
            return obj.date_answer.strftime('%d.%m.%Y')
        elif obj.time_answer:
            return obj.time_answer.strftime('%H:%M')
        return 'Нет ответа'
    answer_display.short_description = 'Ответ'