from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Survey, Question, QuestionChoice, SurveyResponse, Answer


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 1
    fields = ('text', 'order')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'is_required', 'order', 'help_text')
    inlines = [QuestionChoiceInline]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'creator', 'survey_type', 'status', 'is_public', 
        'total_responses_display', 'completion_rate_display', 'created_at'
    )
    
    list_filter = (
        'survey_type', 'status', 'is_public', 'requires_login', 
        'allow_multiple_responses', 'created_at'
    )
    
    search_fields = ('title', 'description', 'creator__username', 'creator__first_name', 'creator__last_name')
    
    readonly_fields = ('id', 'total_responses', 'completion_rate', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'creator')
        }),
        (_('Настройки'), {
            'fields': ('survey_type', 'status', 'is_public', 'requires_login', 'allow_multiple_responses')
        }),
        (_('Временные рамки'), {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        (_('Статистика'), {
            'fields': ('id', 'total_responses', 'completion_rate', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    actions = ['activate_surveys', 'pause_surveys', 'close_surveys', 'make_public', 'make_private']
    
    def total_responses_display(self, obj):
        return format_html(
            '<a href="{}">{} ответов</a>',
            reverse('admin:surveys_surveyresponse_changelist') + f'?survey__id__exact={obj.id}',
            obj.total_responses
        )
    total_responses_display.short_description = 'Ответы'
    
    def completion_rate_display(self, obj):
        color = 'green' if obj.completion_rate >= 70 else 'orange' if obj.completion_rate >= 40 else 'red'
        return format_html(
            '<span style="color: {};">{}%</span>',
            color,
            obj.completion_rate
        )
    completion_rate_display.short_description = 'Завершение'
    
    def activate_surveys(self, request, queryset):
        updated = queryset.update(status=Survey.SurveyStatus.ACTIVE)
        self.message_user(request, f'Активировано {updated} опросов.')
    activate_surveys.short_description = 'Активировать опросы'
    
    def pause_surveys(self, request, queryset):
        updated = queryset.update(status=Survey.SurveyStatus.PAUSED)
        self.message_user(request, f'Приостановлено {updated} опросов.')
    pause_surveys.short_description = 'Приостановить опросы'
    
    def close_surveys(self, request, queryset):
        updated = queryset.update(status=Survey.SurveyStatus.CLOSED)
        self.message_user(request, f'Закрыто {updated} опросов.')
    close_surveys.short_description = 'Закрыть опросы'
    
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'Сделано публичными {updated} опросов.')
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'Сделано приватными {updated} опросов.')
    make_private.short_description = 'Сделать приватными'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'survey', 'question_type', 'is_required', 'order')
    
    list_filter = ('question_type', 'is_required', 'survey__status')
    
    search_fields = ('text', 'survey__title')
    
    ordering = ('survey', 'order')
    
    inlines = [QuestionChoiceInline]
    
    fieldsets = (
        (None, {
            'fields': ('survey', 'text', 'question_type', 'is_required', 'order', 'help_text')
        }),
        (_('Настройки выбора'), {
            'fields': ('min_choices', 'max_choices'),
            'classes': ('collapse',)
        }),
        (_('Настройки шкалы'), {
            'fields': ('min_value', 'max_value'),
            'classes': ('collapse',)
        }),
    )
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Вопрос'


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'order')
    
    list_filter = ('question__question_type',)
    
    search_fields = ('text', 'question__text')
    
    ordering = ('question', 'order')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'get_answer_display')
    fields = ('question', 'get_answer_display')
    
    def get_answer_display(self, obj):
        return obj.get_answer_display()
    get_answer_display.short_description = 'Ответ'


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = (
        'survey', 'user_display', 'ip_address', 'is_completed', 
        'started_at', 'completed_at'
    )
    
    list_filter = ('survey__status', 'is_completed', 'started_at')
    
    search_fields = ('survey__title', 'user__username', 'anonymous_id', 'ip_address')
    
    readonly_fields = ('survey', 'user', 'anonymous_id', 'ip_address', 'user_agent', 'started_at')
    
    inlines = [AnswerInline]
    
    fieldsets = (
        (None, {
            'fields': ('survey', 'user', 'anonymous_id')
        }),
        (_('Техническая информация'), {
            'fields': ('ip_address', 'user_agent', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        (_('Статус'), {
            'fields': ('is_completed',)
        }),
    )
    
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_customuser_change', args=[obj.user.id]),
                obj.user.username
            )
        else:
            return format_html(
                '<span style="color: #666;">Анонимный ({})</span>',
                obj.anonymous_id[:8]
            )
    user_display.short_description = 'Пользователь'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'answer_display')
    
    list_filter = ('question__question_type', 'created_at')
    
    search_fields = ('response__survey__title', 'question__text')
    
    readonly_fields = ('response', 'question', 'created_at')
    
    fieldsets = (
        (None, {
            'fields': ('response', 'question')
        }),
        (_('Ответ'), {
            'fields': ('text_answer', 'selected_choices', 'numeric_answer', 
                      'date_answer', 'time_answer', 'datetime_answer')
        }),
        (_('Система'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def answer_display(self, obj):
        return obj.get_answer_display()
    answer_display.short_description = 'Ответ'