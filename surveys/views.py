from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Survey


def survey_list(request):
    """Список опросов"""
    surveys = Survey.objects.filter(status='active').order_by('-created_at')
    context = {
        'surveys': surveys,
        'title': 'Список опросов'
    }
    return render(request, 'surveys/list.html', context)


@login_required
def dashboard(request):
    """Дашборд пользователя"""
    user_surveys = Survey.objects.filter(creator=request.user).order_by('-created_at')
    context = {
        'surveys': user_surveys,
        'title': 'Мой дашборд'
    }
    return render(request, 'surveys/dashboard.html', context)


@login_required
def survey_create(request):
    """Создание опроса"""
    if not request.user.can_create_surveys and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на создание опросов.')
        return redirect('surveys:dashboard')
    
    if request.method == 'POST':
        # Здесь будет логика создания опроса
        messages.success(request, 'Опрос создан успешно!')
        return redirect('surveys:dashboard')
    
    context = {
        'title': 'Создать опрос'
    }
    return render(request, 'surveys/create.html', context)


def survey_detail(request, pk):
    """Детали опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    context = {
        'survey': survey,
        'title': survey.title
    }
    return render(request, 'surveys/detail.html', context)


@login_required
def survey_edit(request, pk):
    """Редактирование опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if survey.creator != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на редактирование этого опроса.')
        return redirect('surveys:detail', pk=pk)
    
    context = {
        'survey': survey,
        'title': f'Редактировать: {survey.title}'
    }
    return render(request, 'surveys/edit.html', context)


@login_required
def survey_delete(request, pk):
    """Удаление опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if survey.creator != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на удаление этого опроса.')
        return redirect('surveys:detail', pk=pk)
    
    if request.method == 'POST':
        survey.delete()
        messages.success(request, 'Опрос удален успешно!')
        return redirect('surveys:dashboard')
    
    context = {
        'survey': survey,
        'title': f'Удалить: {survey.title}'
    }
    return render(request, 'surveys/delete.html', context)


def survey_take(request, pk):
    """Прохождение опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if survey.login_required and not request.user.is_authenticated:
        messages.error(request, 'Для прохождения этого опроса требуется авторизация.')
        return redirect('users:login')
    
    context = {
        'survey': survey,
        'title': f'Пройти опрос: {survey.title}'
    }
    return render(request, 'surveys/take.html', context)


@login_required
def survey_results(request, pk):
    """Результаты опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if survey.creator != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на просмотр результатов этого опроса.')
        return redirect('surveys:detail', pk=pk)
    
    context = {
        'survey': survey,
        'title': f'Результаты: {survey.title}'
    }
    return render(request, 'surveys/results.html', context)