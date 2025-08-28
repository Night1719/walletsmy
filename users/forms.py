from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию'
        })
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите отдел'
        })
    )
    
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите должность'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите телефон'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'department', 'position', 'phone', 'password1', 'password2'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Стилизация полей
        for field_name in ['username', 'password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[field_name].help_text
                })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Пользователь с таким email уже существует.'))
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """Форма аутентификации"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя или email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'theme_preference']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе...'
            }),
            'theme_preference': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department', 'position', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }


class PasswordChangeForm(forms.Form):
    """Форма смены пароля"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Текущий пароль'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Новый пароль'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(_('Пароли не совпадают.'))
        
        return cleaned_data


class LDAPImportForm(forms.Form):
    """Форма импорта пользователей из LDAP"""
    
    ldap_server = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ldap://your-server.com:389'
        }),
        help_text=_('Адрес LDAP сервера')
    )
    
    bind_dn = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'cn=admin,dc=example,dc=com'
        }),
        help_text=_('DN для привязки к LDAP')
    )
    
    bind_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль для привязки'
        }),
        help_text=_('Пароль для привязки к LDAP')
    )
    
    search_base = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ou=users,dc=example,dc=com'
        }),
        help_text=_('База поиска пользователей')
    )
    
    search_filter = forms.CharField(
        max_length=500,
        initial='(objectClass=person)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(objectClass=person)'
        }),
        help_text=_('Фильтр поиска пользователей')
    )
    
    default_role = forms.ChoiceField(
        choices=CustomUser.UserRole.choices,
        initial=CustomUser.UserRole.USER,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text=_('Роль по умолчанию для импортируемых пользователей')
    )
    
    can_create_surveys = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text=_('Разрешить создание опросов импортированным пользователям')
    )
    
    def clean_ldap_server(self):
        server = self.cleaned_data.get('ldap_server')
        if not server.startswith(('ldap://', 'ldaps://')):
            raise forms.ValidationError(_('LDAP сервер должен начинаться с ldap:// или ldaps://'))
        return server