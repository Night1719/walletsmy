from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Survey, Question, QuestionChoice


class SurveyForm(forms.ModelForm):
    """Форма создания/редактирования опроса"""
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'survey_type', 'status', 'is_public',
            'requires_login', 'allow_multiple_responses', 'start_date', 'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название опроса'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите опрос...'
            }),
            'survey_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_login': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_multiple_responses': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }


class QuestionForm(forms.ModelForm):
    """Форма создания/редактирования вопроса"""
    
    class Meta:
        model = Question
        fields = [
            'text', 'question_type', 'is_required', 'order', 'help_text',
            'min_choices', 'max_choices', 'min_value', 'max_value'
        ]
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите текст вопроса'
            }),
            'question_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'help_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Подсказка для отвечающего (необязательно)'
            }),
            'min_choices': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'max_choices': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'min_value': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'max_value': forms.NumberInput(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['min_choices'].required = False
        self.fields['max_choices'].required = False
        self.fields['min_value'].required = False
        self.fields['max_value'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        min_choices = cleaned_data.get('min_choices')
        max_choices = cleaned_data.get('max_choices')
        min_value = cleaned_data.get('min_value')
        max_value = cleaned_data.get('max_value')
        
        # Валидация для вопросов с выбором
        if question_type in [Question.QuestionType.SINGLE_CHOICE, Question.QuestionType.MULTIPLE_CHOICE]:
            if min_choices and max_choices and min_choices > max_choices:
                raise forms.ValidationError(_('Минимальное количество выборов не может быть больше максимального.'))
        
        # Валидация для рейтингов и шкал
        if question_type in [Question.QuestionType.RATING, Question.QuestionType.SCALE]:
            if min_value and max_value and min_value >= max_value:
                raise forms.ValidationError(_('Минимальное значение должно быть меньше максимального.'))
        
        return cleaned_data


class QuestionChoiceForm(forms.ModelForm):
    """Форма создания/редактирования варианта ответа"""
    
    class Meta:
        model = QuestionChoice
        fields = ['text', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите вариант ответа'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            })
        }


class QuestionChoiceFormSet(forms.BaseInlineFormSet):
    """FormSet для вариантов ответов"""
    
    def clean(self):
        super().clean()
        
        # Проверяем, что есть хотя бы один вариант
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) 
                  for form in self.forms):
            raise forms.ValidationError(_('Должен быть хотя бы один вариант ответа.'))
        
        # Проверяем уникальность текста вариантов
        texts = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                text = form.cleaned_data.get('text', '').strip()
                if text in texts:
                    raise forms.ValidationError(_('Варианты ответов должны быть уникальными.'))
                texts.append(text)


QuestionChoiceInlineFormSet = forms.inlineformset_factory(
    Question,
    QuestionChoice,
    form=QuestionChoiceForm,
    formset=QuestionChoiceFormSet,
    extra=1,
    can_delete=True
)


class SurveyResponseForm(forms.Form):
    """Форма ответа на опрос"""
    
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = survey
        
        # Динамически создаем поля для каждого вопроса
        for question in survey.questions.all().order_by('order'):
            field_name = f'question_{question.id}'
            
            if question.question_type == Question.QuestionType.TEXT:
                self.fields[field_name] = forms.CharField(
                    max_length=500,
                    required=question.is_required,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Введите ответ'
                    })
                )
            
            elif question.question_type == Question.QuestionType.TEXTAREA:
                self.fields[field_name] = forms.CharField(
                    max_length=2000,
                    required=question.is_required,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': 'Введите ответ'
                    })
                )
            
            elif question.question_type == Question.QuestionType.SINGLE_CHOICE:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=question.is_required,
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    })
                )
            
            elif question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices,
                    required=question.is_required,
                    widget=forms.CheckboxSelectMultiple(attrs={
                        'class': 'form-check-input'
                    })
                )
            
            elif question.question_type == Question.QuestionType.RATING:
                choices = [(i, str(i)) for i in range(question.min_value, question.max_value + 1)]
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=question.is_required,
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    })
                )
            
            elif question.question_type == Question.QuestionType.SCALE:
                self.fields[field_name] = forms.IntegerField(
                    min_value=question.min_value,
                    max_value=question.max_value,
                    required=question.is_required,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'min': question.min_value,
                        'max': question.max_value
                    })
                )
            
            elif question.question_type == Question.QuestionType.DATE:
                self.fields[field_name] = forms.DateField(
                    required=question.is_required,
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date'
                    })
                )
            
            elif question.question_type == Question.QuestionType.TIME:
                self.fields[field_name] = forms.TimeField(
                    required=question.is_required,
                    widget=forms.TimeInput(attrs={
                        'class': 'form-control',
                        'type': 'time'
                    })
                )
            
            elif question.question_type == Question.QuestionType.DATETIME:
                self.fields[field_name] = forms.DateTimeField(
                    required=question.is_required,
                    widget=forms.DateTimeInput(attrs={
                        'class': 'form-control',
                        'type': 'datetime-local'
                    })
                )
            
            # Добавляем help_text если есть
            if question.help_text:
                self.fields[field_name].help_text = question.help_text
            
            # Добавляем label
            self.fields[field_name].label = question.text
            if question.is_required:
                self.fields[field_name].label += ' *'