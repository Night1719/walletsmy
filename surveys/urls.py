from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Основные страницы
    path('', views.SurveyListView.as_view(), name='survey_list'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Создание и редактирование опросов
    path('create/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('<uuid:pk>/edit/', views.SurveyEditView.as_view(), name='survey_edit'),
    path('<uuid:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey_delete'),
    
    # Управление вопросами
    path('<uuid:survey_id>/questions/', views.QuestionListView.as_view(), name='question_list'),
    path('<uuid:survey_id>/questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('<uuid:survey_id>/questions/<int:pk>/edit/', views.QuestionEditView.as_view(), name='question_edit'),
    path('<uuid:survey_id>/questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    
    # Прохождение опросов
    path('<uuid:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
    path('<uuid:pk>/take/', views.SurveyTakeView.as_view(), name='survey_take'),
    path('<uuid:pk>/submit/', views.SurveySubmitView.as_view(), name='survey_submit'),
    
    # Публичные ссылки (без авторизации)
    path('public/<uuid:pk>/', views.PublicSurveyView.as_view(), name='public_survey'),
    path('public/<uuid:pk>/take/', views.PublicSurveyTakeView.as_view(), name='public_survey_take'),
    path('public/<uuid:pk>/submit/', views.PublicSurveySubmitView.as_view(), name='public_survey_submit'),
    
    # Результаты и аналитика
    path('<uuid:pk>/results/', views.SurveyResultsView.as_view(), name='survey_results'),
    path('<uuid:pk>/results/export/', views.SurveyResultsExportView.as_view(), name='survey_results_export'),
    path('<uuid:pk>/analytics/', views.SurveyAnalyticsView.as_view(), name='survey_analytics'),
    
    # API для AJAX
    path('api/surveys/', views.SurveyListAPIView.as_view(), name='survey_list_api'),
    path('api/surveys/<uuid:pk>/', views.SurveyDetailAPIView.as_view(), name='survey_detail_api'),
    path('api/surveys/<uuid:pk>/questions/', views.QuestionListAPIView.as_view(), name='question_list_api'),
    path('api/surveys/<uuid:pk>/responses/', views.ResponseListAPIView.as_view(), name='response_list_api'),
]