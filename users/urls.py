from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Профиль пользователя
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Админ функции
    path('admin/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin/users/create/', views.AdminCreateUserView.as_view(), name='admin_create_user'),
    path('admin/users/<int:pk>/edit/', views.AdminEditUserView.as_view(), name='admin_edit_user'),
    path('admin/users/<int:pk>/delete/', views.AdminDeleteUserView.as_view(), name='admin_delete_user'),
    path('admin/ldap-import/', views.LDAPImportView.as_view(), name='ldap_import'),
    
    # API для AJAX
    path('api/users/', views.UserListAPIView.as_view(), name='user_list_api'),
    path('api/users/<int:pk>/', views.UserDetailAPIView.as_view(), name='user_detail_api'),
]