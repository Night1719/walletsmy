from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.survey_list, name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.survey_create, name='create'),
    path('<uuid:pk>/', views.survey_detail, name='detail'),
    path('<uuid:pk>/edit/', views.survey_edit, name='edit'),
    path('<uuid:pk>/delete/', views.survey_delete, name='delete'),
    path('<uuid:pk>/take/', views.survey_take, name='take'),
    path('<uuid:pk>/results/', views.survey_results, name='results'),
]