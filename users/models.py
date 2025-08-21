from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с расширенными полями"""
    
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Отдел'
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Должность'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    
    is_ldap_user = models.BooleanField(
        default=False,
        verbose_name='Пользователь LDAP'
    )
    
    ldap_dn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='LDAP DN'
    )
    
    can_create_surveys = models.BooleanField(
        default=False,
        verbose_name='Может создавать опросы'
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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_moderator(self):
        return self.role in ['admin', 'moderator']


class UserProfile(models.Model):
    """Профиль пользователя с дополнительной информацией"""
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    
    theme_preference = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Светлая'),
            ('dark', 'Темная'),
            ('auto', 'Авто'),
        ],
        default='auto',
        verbose_name='Предпочитаемая тема'
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
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Автоматически создаем профиль при создании пользователя
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)