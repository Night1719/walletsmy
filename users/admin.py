from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ('bio', 'avatar', 'theme_preference')


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 
        'department', 'can_create_surveys', 'is_active', 'date_joined'
    )
    
    list_filter = (
        'role', 'department', 'can_create_surveys', 'is_active', 
        'is_staff', 'is_superuser', 'is_ldap_user', 'date_joined'
    )
    
    search_fields = ('username', 'first_name', 'last_name', 'email', 'department')
    
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Личная информация'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Рабочая информация'), {
            'fields': ('department', 'position', 'role', 'can_create_surveys')
        }),
        (_('LDAP информация'), {
            'fields': ('is_ldap_user', 'ldap_dn'),
            'classes': ('collapse',)
        }),
        (_('Разрешения'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'first_name', 
                'last_name', 'role', 'department', 'can_create_surveys'
            ),
        }),
    )
    
    actions = ['enable_survey_creation', 'disable_survey_creation', 'activate_users', 'deactivate_users']
    
    def enable_survey_creation(self, request, queryset):
        updated = queryset.update(can_create_surveys=True)
        self.message_user(request, f'Включено создание опросов для {updated} пользователей.')
    enable_survey_creation.short_description = 'Включить создание опросов'
    
    def disable_survey_creation(self, request, queryset):
        updated = queryset.update(can_create_surveys=False)
        self.message_user(request, f'Отключено создание опросов для {updated} пользователей.')
    disable_survey_creation.short_description = 'Отключить создание опросов'
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} пользователей.')
    activate_users.short_description = 'Активировать пользователей'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} пользователей.')
    deactivate_users.short_description = 'Деактивировать пользователей'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_preference', 'created_at')
    list_filter = ('theme_preference',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Профиль'), {'fields': ('bio', 'avatar')}),
        (_('Настройки'), {'fields': ('theme_preference',)}),
        (_('Система'), {'fields': ('created_at',), 'classes': ('collapse',)}),
    )