from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import json

from .models import CustomUser, UserProfile
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    UserUpdateForm, PasswordChangeForm, LDAPImportForm
)
from .ldap_utils import LDAPImporter


def is_admin(user):
    """Проверяет, является ли пользователь администратором"""
    return user.is_authenticated and user.is_admin


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('surveys:list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('users:login')


@login_required
def profile_view(request):
    """Профиль пользователя"""
    return render(request, 'users/profile.html')


@login_required
def profile_edit_view(request):
    """Представление редактирования профиля"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Профиль успешно обновлен!'))
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile_edit.html', context)


@login_required
def change_password_view(request):
    """Представление смены пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password1']
            
            if request.user.check_password(current_password):
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, _('Пароль успешно изменен!'))
                return redirect('users:profile')
            else:
                form.add_error('current_password', _('Неверный текущий пароль'))
    else:
        form = PasswordChangeForm()
    
    context = {'form': form}
    return render(request, 'users/change_password.html', context)


@user_passes_test(is_admin)
def admin_users_view(request):
    """Представление управления пользователями для админов"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    # Фильтрация по роли
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Пагинация
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'roles': CustomUser.UserRole.choices
    }
    return render(request, 'users/admin_users.html', context)


@user_passes_test(is_admin)
def admin_create_user_view(request):
    """Представление создания пользователя для админов"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Даем доступ к админке
            user.save()
            
            # Создаем профиль
            UserProfile.objects.create(user=user)
            
            messages.success(request, _('Пользователь успешно создан!'))
            return redirect('users:admin_users')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'users/admin_create_user.html', context)


@user_passes_test(is_admin)
def admin_edit_user_view(request, pk):
    """Представление редактирования пользователя для админов"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Пользователь успешно обновлен!'))
            return redirect('users:admin_users')
    else:
        form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'roles': CustomUser.UserRole.choices
    }
    return render(request, 'users/admin_edit_user.html', context)


@user_passes_test(is_admin)
def admin_delete_user_view(request, pk):
    """Представление удаления пользователя для админов"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, _('Вы не можете удалить свой собственный аккаунт!'))
        else:
            user.delete()
            messages.success(request, _('Пользователь успешно удален!'))
        return redirect('users:admin_users')
    
    context = {'user': user}
    return render(request, 'users/admin_delete_user.html', context)


@user_passes_test(is_admin)
def ldap_import_view(request):
    """Представление импорта пользователей из LDAP"""
    if request.method == 'POST':
        form = LDAPImportForm(request.POST)
        if form.is_valid():
            try:
                # Получаем данные формы
                ldap_config = {
                    'server_uri': form.cleaned_data['ldap_server'],
                    'bind_dn': form.cleaned_data['bind_dn'],
                    'bind_password': form.cleaned_data['bind_password'],
                    'search_base': form.cleaned_data['search_base'],
                    'search_filter': form.cleaned_data['search_filter'],
                    'default_role': form.cleaned_data['default_role'],
                    'can_create_surveys': form.cleaned_data['can_create_surveys']
                }
                
                # Импортируем пользователей
                importer = LDAPImporter(ldap_config)
                imported_count, errors = importer.import_users()
                
                if imported_count > 0:
                    messages.success(
                        request, 
                        _('Успешно импортировано {} пользователей из LDAP').format(imported_count)
                    )
                
                if errors:
                    for error in errors:
                        messages.warning(request, error)
                
                return redirect('users:admin_users')
                
            except Exception as e:
                messages.error(request, _('Ошибка импорта: {}').format(str(e)))
    else:
        form = LDAPImportForm()
    
    context = {'form': form}
    return render(request, 'users/ldap_import.html', context)


# API представления для AJAX
@method_decorator(csrf_exempt, name='dispatch')
class UserListAPIView(ListView):
    """API для получения списка пользователей"""
    model = CustomUser
    template_name = None
    
    def get_queryset(self):
        queryset = CustomUser.objects.all()
        
        # Фильтрация
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Роль
        role = self.request.GET.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset[:50]  # Ограничиваем количество
    
    def render_to_response(self, context, **response_kwargs):
        users_data = []
        for user in context['object_list']:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.get_role_display(),
                'department': user.department,
                'is_active': user.is_active,
                'can_create_surveys': user.can_create_surveys,
                'date_joined': user.date_joined.strftime('%d.%m.%Y %H:%M') if user.date_joined else ''
            })
        
        return JsonResponse({
            'users': users_data,
            'total': len(users_data)
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailAPIView(DetailView):
    """API для получения детальной информации о пользователе"""
    model = CustomUser
    template_name = None
    
    def render_to_response(self, context, **response_kwargs):
        user = context['object']
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.get_role_display(),
            'department': user.department,
            'position': user.position,
            'phone': user.phone,
            'is_active': user.is_active,
            'can_create_surveys': user.can_create_surveys,
            'is_ldap_user': user.is_ldap_user,
            'date_joined': user.date_joined.strftime('%d.%m.%Y %H:%M') if user.date_joined else '',
            'last_login': user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else ''
        }
        
        return JsonResponse(user_data)


@require_http_methods(["POST"])
@user_passes_test(is_admin)
def toggle_user_status(request, pk):
    """API для переключения статуса пользователя"""
    try:
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': _('Статус пользователя изменен')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
@user_passes_test(is_admin)
def toggle_survey_creation(request, pk):
    """API для переключения права создания опросов"""
    try:
        user = get_object_or_404(CustomUser, pk=pk)
        user.can_create_surveys = not user.can_create_surveys
        user.save()
        
        return JsonResponse({
            'success': True,
            'can_create_surveys': user.can_create_surveys,
            'message': _('Право создания опросов изменено')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
@user_passes_test(is_admin)
def bulk_user_actions(request):
    """API для массовых действий с пользователями"""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return JsonResponse({
                'success': False,
                'error': _('Не выбраны пользователи')
            })
        
        users = CustomUser.objects.filter(id__in=user_ids)
        
        if action == 'activate':
            users.update(is_active=True)
            message = _('Пользователи активированы')
        elif action == 'deactivate':
            users.update(is_active=False)
            message = _('Пользователи деактивированы')
        elif action == 'enable_surveys':
            users.update(can_create_surveys=True)
            message = _('Право создания опросов включено')
        elif action == 'disable_surveys':
            users.update(can_create_surveys=False)
            message = _('Право создания опросов отключено')
        else:
            return JsonResponse({
                'success': False,
                'error': _('Неизвестное действие')
            })
        
        return JsonResponse({
            'success': True,
            'message': message,
            'affected_count': len(user_ids)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })