from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('Имя')
        )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label=_('Фамилия')
        )
    username = forms.CharField(
        max_length=150,
        required=True,
        label=_('Имя пользователя')
        )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']
        labels = {
            'password1': _('Пароль'),
            'password2': _('Подтверждение пароля'),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = _('Пароль минимум 8 символов')
        self.fields['password2'].help_text = None

class LoginForm(AuthenticationForm):
    pass
