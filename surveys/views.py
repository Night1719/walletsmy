from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import csv
import json
import uuid

from .models import Survey, Question, QuestionChoice, SurveyResponse, Answer
from .forms import SurveyForm, QuestionForm, SurveyResponseForm
from users.models import CustomUser


def is_survey_creator(user):
    """Проверяет, может ли пользователь создавать опросы"""
    return user.is_authenticated and user.has_survey_permission('create')


class SurveyListView(ListView):
    """Представление списка опросов"""
    model = Survey
    template_name = 'surveys/survey_list.html'
    context_object_name = 'surveys'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Survey.objects.filter(status=Survey.SurveyStatus.ACTIVE)
        
        # Поиск
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Фильтрация по типу
        survey_type = self.request.GET.get('type', '')
        if survey_type:
            queryset = queryset.filter(survey_type=survey_type)
        
        # Фильтрация по публичности
        if self.request.user.is_authenticated:
            # Авторизованные пользователи видят все активные опросы
            pass
        else:
            # Неавторизованные видят только публичные
            queryset = queryset.filter(is_public=True)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_types'] = Survey.SurveyType.choices
        context['search_query'] = self.request.GET.get('search', '')
        context['type_filter'] = self.request.GET.get('type', '')
        return context


@login_required
def dashboard_view(request):
    """Дашборд для авторизованных пользователей"""
    user = request.user
    
    # Опросы пользователя
    if user.is_survey_creator:
        created_surveys = Survey.objects.filter(creator=user).order_by('-created_at')[:5]
        draft_surveys = Survey.objects.filter(
            creator=user, 
            status=Survey.SurveyStatus.DRAFT
        ).order_by('-created_at')[:5]
    else:
        created_surveys = []
        draft_surveys = []
    
    # Активные опросы для прохождения
    active_surveys = Survey.objects.filter(
        status=Survey.SurveyStatus.ACTIVE
    ).exclude(creator=user).order_by('-created_at')[:5]
    
    # Статистика
    if user.is_survey_creator:
        total_surveys = Survey.objects.filter(creator=user).count()
        total_responses = SurveyResponse.objects.filter(
            survey__creator=user
        ).count()
        avg_completion = Survey.objects.filter(creator=user).aggregate(
            avg=Avg('completion_rate')
        )['avg'] or 0
    else:
        total_surveys = 0
        total_responses = 0
        avg_completion = 0
    
    # Недавние ответы на опросы пользователя
    if user.is_survey_creator:
        recent_responses = SurveyResponse.objects.filter(
            survey__creator=user
        ).order_by('-started_at')[:5]
    else:
        recent_responses = []
    
    context = {
        'created_surveys': created_surveys,
        'draft_surveys': draft_surveys,
        'active_surveys': active_surveys,
        'recent_responses': recent_responses,
        'total_surveys': total_surveys,
        'total_responses': total_responses,
        'avg_completion': round(avg_completion, 1)
    }
    
    return render(request, 'surveys/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_survey_creator), name='dispatch')
class SurveyCreateView(CreateView):
    """Представление создания опроса"""
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    success_url = reverse_lazy('surveys:dashboard')
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _('Опрос успешно создан! Теперь добавьте вопросы.'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'create'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_survey_creator), name='dispatch')
class SurveyEditView(UpdateView):
    """Представление редактирования опроса"""
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    
    def get_queryset(self):
        # Пользователь может редактировать только свои опросы
        return Survey.objects.filter(creator=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('surveys:survey_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Опрос успешно обновлен!'))
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'edit'
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_survey_creator), name='dispatch')
class SurveyDeleteView(DeleteView):
    """Представление удаления опроса"""
    model = Survey
    template_name = 'surveys/survey_confirm_delete.html'
    success_url = reverse_lazy('surveys:dashboard')
    
    def get_queryset(self):
        # Пользователь может удалять только свои опросы
        return Survey.objects.filter(creator=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Опрос успешно удален!'))
        return super().delete(request, *args, **kwargs)


class SurveyDetailView(DetailView):
    """Представление детального просмотра опроса"""
    model = Survey
    template_name = 'surveys/survey_detail.html'
    context_object_name = 'survey'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.object
        
        # Проверяем доступ
        if not survey.is_public and not self.request.user.is_authenticated:
            context['access_denied'] = True
            return context
        
        if survey.requires_login and not self.request.user.is_authenticated:
            context['login_required'] = True
            return context
        
        # Добавляем вопросы
        context['questions'] = survey.questions.all().order_by('order')
        
        # Проверяем, проходил ли пользователь опрос
        if self.request.user.is_authenticated:
            context['has_responded'] = survey.responses.filter(
                user=self.request.user
            ).exists()
        else:
            context['has_responded'] = False
        
        # Статистика
        context['total_responses'] = survey.total_responses
        context['completion_rate'] = survey.completion_rate
        
        return context


@login_required
def survey_take_view(request, pk):
    """Представление прохождения опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # Проверяем доступ
    if not survey.is_active:
        messages.error(request, _('Этот опрос неактивен.'))
        return redirect('surveys:survey_detail', pk=pk)
    
    if survey.requires_login and not request.user.is_authenticated:
        messages.error(request, _('Для прохождения этого опроса требуется авторизация.'))
        return redirect('users:login')
    
    # Проверяем, проходил ли пользователь опрос
    if not survey.allow_multiple_responses:
        existing_response = SurveyResponse.objects.filter(
            survey=survey,
            user=request.user
        ).first()
        
        if existing_response:
            messages.warning(request, _('Вы уже проходили этот опрос.'))
            return redirect('surveys:survey_detail', pk=pk)
    
    # Создаем форму ответа
    if request.method == 'POST':
        form = SurveyResponseForm(survey, request.POST)
        if form.is_valid():
            # Создаем ответ на опрос
            response = SurveyResponse.objects.create(
                survey=survey,
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_completed=True,
                completed_at=timezone.now()
            )
            
            # Сохраняем ответы на вопросы
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    
                    answer = Answer.objects.create(
                        response=response,
                        question=question
                    )
                    
                    # Заполняем ответ в зависимости от типа вопроса
                    if question.question_type == Question.QuestionType.TEXT:
                        answer.text_answer = value
                    elif question.question_type == Question.QuestionType.TEXTAREA:
                        answer.text_answer = value
                    elif question.question_type == Question.QuestionType.SINGLE_CHOICE:
                        choice = QuestionChoice.objects.get(id=value)
                        answer.selected_choices.add(choice)
                    elif question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
                        for choice_id in value:
                            choice = QuestionChoice.objects.get(id=choice_id)
                            answer.selected_choices.add(choice)
                    elif question.question_type == Question.QuestionType.RATING:
                        answer.numeric_answer = int(value)
                    elif question.question_type == Question.QuestionType.SCALE:
                        answer.numeric_answer = value
                    elif question.question_type == Question.QuestionType.DATE:
                        answer.date_answer = value
                    elif question.question_type == Question.QuestionType.TIME:
                        answer.time_answer = value
                    elif question.question_type == Question.QuestionType.DATETIME:
                        answer.datetime_answer = value
                    
                    answer.save()
            
            messages.success(request, _('Спасибо! Ваш ответ на опрос сохранен.'))
            return redirect('surveys:survey_detail', pk=pk)
    else:
        form = SurveyResponseForm(survey)
    
    context = {
        'survey': survey,
        'form': form
    }
    
    return render(request, 'surveys/survey_take.html', context)


def public_survey_view(request, pk):
    """Представление публичного опроса (без авторизации)"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # Проверяем, что опрос публичный
    if not survey.is_public:
        messages.error(request, _('Этот опрос недоступен публично.'))
        return redirect('surveys:survey_list')
    
    # Проверяем активность
    if not survey.is_active:
        messages.error(request, _('Этот опрос неактивен.'))
        return redirect('surveys:survey_list')
    
    context = {
        'survey': survey,
        'questions': survey.questions.all().order_by('order'),
        'is_public': True
    }
    
    return render(request, 'surveys/public_survey.html', context)


def public_survey_take_view(request, pk):
    """Представление прохождения публичного опроса"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # Проверяем доступ
    if not survey.is_public or not survey.is_active:
        messages.error(request, _('Опрос недоступен.'))
        return redirect('surveys:survey_list')
    
    # Создаем форму ответа
    if request.method == 'POST':
        form = SurveyResponseForm(survey, request.POST)
        if form.is_valid():
            # Создаем анонимный ответ
            response = SurveyResponse.objects.create(
                survey=survey,
                user=None,  # Анонимный пользователь
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_completed=True,
                completed_at=timezone.now()
            )
            
            # Сохраняем ответы (аналогично survey_take_view)
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    
                    answer = Answer.objects.create(
                        response=response,
                        question=question
                    )
                    
                    # Заполняем ответ (код аналогичен survey_take_view)
                    if question.question_type == Question.QuestionType.TEXT:
                        answer.text_answer = value
                    elif question.question_type == Question.QuestionType.TEXTAREA:
                        answer.text_answer = value
                    elif question.question_type == Question.QuestionType.SINGLE_CHOICE:
                        choice = QuestionChoice.objects.get(id=value)
                        answer.selected_choices.add(choice)
                    elif question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
                        for choice_id in value:
                            choice = QuestionChoice.objects.get(id=choice_id)
                            answer.selected_choices.add(choice)
                    elif question.question_type == Question.QuestionType.RATING:
                        answer.numeric_answer = int(value)
                    elif question.question_type == Question.QuestionType.SCALE:
                        answer.numeric_answer = value
                    elif question.question_type == Question.QuestionType.DATE:
                        answer.date_answer = value
                    elif question.question_type == Question.QuestionType.TIME:
                        answer.time_answer = value
                    elif question.question_type == Question.QuestionType.DATETIME:
                        answer.datetime_answer = value
                    
                    answer.save()
            
            messages.success(request, _('Спасибо! Ваш ответ на опрос сохранен.'))
            return redirect('surveys:public_survey', pk=pk)
    else:
        form = SurveyResponseForm(survey)
    
    context = {
        'survey': survey,
        'form': form,
        'is_public': True
    }
    
    return render(request, 'surveys/public_survey_take.html', context)


@login_required
@user_passes_test(is_survey_creator)
def survey_results_view(request, pk):
    """Представление результатов опроса"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    
    # Получаем все ответы
    responses = survey.responses.all()
    
    # Статистика по вопросам
    questions_stats = []
    for question in survey.questions.all().order_by('order'):
        answers = Answer.objects.filter(
            response__survey=survey,
            question=question
        )
        
        if question.question_type in [Question.QuestionType.SINGLE_CHOICE, Question.QuestionType.MULTIPLE_CHOICE]:
            # Статистика по вариантам ответов
            choice_stats = {}
            for choice in question.choices.all():
                count = answers.filter(selected_choices=choice).count()
                choice_stats[choice.text] = count
            
            questions_stats.append({
                'question': question,
                'type': 'choice',
                'choice_stats': choice_stats,
                'total_answers': answers.count()
            })
        
        elif question.question_type in [Question.QuestionType.RATING, Question.QuestionType.SCALE]:
            # Статистика по числовым ответам
            numeric_answers = [a.numeric_answer for a in answers if a.numeric_answer is not None]
            if numeric_answers:
                avg = sum(numeric_answers) / len(numeric_answers)
                min_val = min(numeric_answers)
                max_val = max(numeric_answers)
            else:
                avg = min_val = max_val = 0
            
            questions_stats.append({
                'question': question,
                'type': 'numeric',
                'average': round(avg, 2),
                'min': min_val,
                'max': max_val,
                'total_answers': len(numeric_answers)
            })
        
        else:
            # Для текстовых ответов показываем количество
            questions_stats.append({
                'question': question,
                'type': 'text',
                'total_answers': answers.count()
            })
    
    context = {
        'survey': survey,
        'questions_stats': questions_stats,
        'total_responses': responses.count(),
        'completed_responses': responses.filter(is_completed=True).count(),
        'completion_rate': survey.completion_rate
    }
    
    return render(request, 'surveys/survey_results.html', context)


@login_required
@user_passes_test(is_survey_creator)
def survey_results_export_view(request, pk):
    """Экспорт результатов опроса"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="survey_{pk}_results.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Вопрос', 'Ответ', 'Пользователь', 'IP адрес', 'Время ответа'])
        
        for question in survey.questions.all():
            answers = Answer.objects.filter(
                response__survey=survey,
                question=question
            )
            
            for answer in answers:
                response_obj = answer.response
                user_info = response_obj.user.username if response_obj.user else 'Анонимный'
                
                writer.writerow([
                    question.text,
                    answer.get_answer_display(),
                    user_info,
                    response_obj.ip_address,
                    answer.created_at.strftime('%d.%m.%Y %H:%M')
                ])
        
        return response
    
    else:
        messages.error(request, _('Неподдерживаемый формат экспорта.'))
        return redirect('surveys:survey_results', pk=pk)


@login_required
@user_passes_test(is_survey_creator)
def survey_analytics_view(request, pk):
    """Представление аналитики опроса"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    
    # Получаем данные для графиков
    responses_by_date = survey.responses.extra(
        select={'date': 'date(started_at)'}
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Данные для круговой диаграммы по типам вопросов
    question_types = survey.questions.values('question_type').annotate(
        count=Count('id')
    )
    
    context = {
        'survey': survey,
        'responses_by_date': list(responses_by_date),
        'question_types': list(question_types),
        'total_responses': survey.total_responses,
        'completion_rate': survey.completion_rate
    }
    
    return render(request, 'surveys/survey_analytics.html', context)


# API представления для AJAX
@method_decorator(csrf_exempt, name='dispatch')
class SurveyListAPIView(ListView):
    """API для получения списка опросов"""
    model = Survey
    template_name = None
    
    def get_queryset(self):
        queryset = Survey.objects.filter(status=Survey.SurveyStatus.ACTIVE)
        
        # Фильтрация
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Тип опроса
        survey_type = self.request.GET.get('type', '')
        if survey_type:
            queryset = queryset.filter(survey_type=survey_type)
        
        return queryset[:20]  # Ограничиваем количество
    
    def render_to_response(self, context, **response_kwargs):
        surveys_data = []
        for survey in context['object_list']:
            surveys_data.append({
                'id': str(survey.id),
                'title': survey.title,
                'description': survey.description,
                'survey_type': survey.get_survey_type_display(),
                'creator': survey.creator.username,
                'total_responses': survey.total_responses,
                'completion_rate': survey.completion_rate,
                'created_at': survey.created_at.strftime('%d.%m.%Y %H:%M'),
                'url': f'/surveys/{survey.id}/'
            })
        
        return JsonResponse({
            'surveys': surveys_data,
            'total': len(surveys_data)
        })


@method_decorator(csrf_exempt, name='dispatch')
class SurveyDetailAPIView(DetailView):
    """API для получения детальной информации об опросе"""
    model = Survey
    template_name = None
    
    def render_to_response(self, context, **response_kwargs):
        survey = context['object']
        survey_data = {
            'id': str(survey.id),
            'title': survey.title,
            'description': survey.description,
            'survey_type': survey.get_survey_type_display(),
            'status': survey.get_status_display(),
            'creator': survey.creator.username,
            'is_public': survey.is_public,
            'requires_login': survey.requires_login,
            'total_responses': survey.total_responses,
            'completion_rate': survey.completion_rate,
            'created_at': survey.created_at.strftime('%d.%m.%Y %H:%M'),
            'questions_count': survey.questions.count()
        }
        
        return JsonResponse(survey_data)


@method_decorator(csrf_exempt, name='dispatch')
class QuestionListAPIView(ListView):
    """API для получения списка вопросов опроса"""
    model = Question
    template_name = None
    
    def get_queryset(self):
        survey_id = self.kwargs.get('pk')
        return Question.objects.filter(survey_id=survey_id).order_by('order')
    
    def render_to_response(self, context, **response_kwargs):
        questions_data = []
        for question in context['object_list']:
            question_data = {
                'id': question.id,
                'text': question.text,
                'question_type': question.get_question_type_display(),
                'is_required': question.is_required,
                'order': question.order,
                'help_text': question.help_text
            }
            
            # Добавляем варианты ответов для вопросов с выбором
            if question.question_type in [Question.QuestionType.SINGLE_CHOICE, Question.QuestionType.MULTIPLE_CHOICE]:
                question_data['choices'] = [
                    {'id': choice.id, 'text': choice.text, 'order': choice.order}
                    for choice in question.choices.all().order_by('order')
                ]
            
            questions_data.append(question_data)
        
        return JsonResponse({
            'questions': questions_data,
            'total': len(questions_data)
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResponseListAPIView(ListView):
    """API для получения списка ответов на опрос"""
    model = SurveyResponse
    template_name = None
    
    def get_queryset(self):
        survey_id = self.kwargs.get('pk')
        return SurveyResponse.objects.filter(survey_id=survey_id).order_by('-started_at')
    
    def render_to_response(self, context, **response_kwargs):
        responses_data = []
        for response in context['object_list']:
            response_data = {
                'id': response.id,
                'user': response.user.username if response.user else 'Анонимный',
                'ip_address': response.ip_address,
                'is_completed': response.is_completed,
                'started_at': response.started_at.strftime('%d.%m.%Y %H:%M'),
                'completed_at': response.completed_at.strftime('%d.%m.%Y %H:%M') if response.completed_at else None
            }
            
            responses_data.append(response_data)
        
        return JsonResponse({
            'responses': responses_data,
            'total': len(responses_data)
        })