"""
URL configuration for survey_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/surveys/', permanent=False), name='home'),
    path('users/', include('users.urls')),
    path('surveys/', include('surveys.urls')),
]

# Добавляем статические и медиа файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Настройка админки
admin.site.site_header = 'Бантер Групп - Администрирование'
admin.site.site_title = 'BG Опросник'
admin.site.index_title = 'Панель управления'