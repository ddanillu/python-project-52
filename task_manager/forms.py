from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Status

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

# forms.py
class UserForm(forms.ModelForm):
    # ✅ ПУСТЫЕ поля паролей (не обязательные)
    password1 = forms.CharField(
        label=_('Пароль'),
        required=False,
        widget=forms.PasswordInput,
        help_text=_('Оставьте пустым для сохранения текущего')
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        required=False,
        widget=forms.PasswordInput
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        labels = {
            'username': _('Имя пользователя'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
        }
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Пользователь с таким именем уже существует.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
        return user


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
