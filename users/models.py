from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с поддержкой ролей"""
    
    class UserRole(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        SURVEY_CREATOR = 'survey_creator', _('Создатель опросов')
        USER = 'user', _('Пользователь')
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name=_('Роль')
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Отдел')
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Должность')
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Телефон')
    )
    
    is_ldap_user = models.BooleanField(
        default=False,
        verbose_name=_('LDAP пользователь')
    )
    
    ldap_dn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('LDAP DN')
    )
    
    can_create_surveys = models.BooleanField(
        default=False,
        verbose_name=_('Может создавать опросы')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    @property
    def is_admin(self):
        return self.role == self.UserRole.ADMIN
    
    @property
    def is_survey_creator(self):
        return self.role == self.UserRole.SURVEY_CREATOR or self.can_create_surveys
    
    def has_survey_permission(self, permission_type):
        """Проверяет права пользователя на опросы"""
        if self.is_admin:
            return True
        
        if permission_type == 'create':
            return self.is_survey_creator
        
        return True


class UserProfile(models.Model):
    """Дополнительный профиль пользователя"""
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Пользователь')
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name=_('О себе')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )
    
    theme_preference = models.CharField(
        max_length=10,
        choices=[
            ('light', _('Светлая')),
            ('dark', _('Темная')),
            ('auto', _('Авто'))
        ],
        default='auto',
        verbose_name=_('Предпочтение темы')
    )
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f"Профиль {self.user.username}"