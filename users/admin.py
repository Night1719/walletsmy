from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role',
        'department', 'position', 'can_create_surveys', 'is_active'
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
            'fields': ('role', 'department', 'position', 'can_create_surveys')
        }),
        (_('LDAP'), {
            'fields': ('is_ldap_user', 'ldap_dn'),
            'classes': ('collapse',)
        }),
        (_('Разрешения'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'role'),
        }),
    )
    
    actions = ['make_survey_creator', 'remove_survey_creator', 'activate_users', 'deactivate_users']
    
    def make_survey_creator(self, request, queryset):
        """Дать право на создание опросов"""
        updated = queryset.update(can_create_surveys=True)
        self.message_user(
            request,
            f'{updated} пользователей получили право на создание опросов.'
        )
    make_survey_creator.short_description = "Дать право на создание опросов"
    
    def remove_survey_creator(self, request, queryset):
        """Убрать право на создание опросов"""
        updated = queryset.update(can_create_surveys=False)
        self.message_user(
            request,
            f'{updated} пользователей лишены права на создание опросов.'
        )
    remove_survey_creator.short_description = "Убрать право на создание опросов"
    
    def activate_users(self, request, queryset):
        """Активировать пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} пользователей активировано.'
        )
    activate_users.short_description = "Активировать пользователей"
    
    def deactivate_users(self, request, queryset):
        """Деактивировать пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} пользователей деактивировано.'
        )
    deactivate_users.short_description = "Деактивировать пользователей"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_preference', 'created_at', 'updated_at')
    list_filter = ('theme_preference', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'avatar', 'theme_preference')
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Регистрируем модели
admin.site.register(CustomUser, CustomUserAdmin)