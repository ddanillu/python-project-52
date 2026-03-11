from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Status, Task, Label


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, label=_("Имя"))
    last_name = forms.CharField(
        max_length=150, required=False, label=_("Фамилия")
    )
    username = forms.CharField(
        max_length=150, required=True, label=_("Имя пользователя")
    )
    password_confirm = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput,
        help_text=None,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password1",
            "password_confirm",
        ]
        labels = {
            "password1": _("Пароль"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("password2", None)
        self.fields["password1"].help_text = _("Пароль минимум 3 символов")
        self.fields["password_confirm"].help_text = None

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password_confirm")

        # Проверка на совпадение паролей
        if password1 and password2 and password1 != password2:
            self.add_error("password_confirm", _("Пароли не совпадают"))

        # Проверка длины пароля
        if password1 and len(password1) < 3:
            raise forms.ValidationError(
                _("Пароль должен содержать минимум 3 символа")
            )

        return cleaned_data


class LoginForm(AuthenticationForm):
    pass


class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_("Пароль"),
        required=False,
        widget=forms.PasswordInput,
        help_text=_("Оставьте пустым для сохранения текущего"),
    )
    password_confirm = forms.CharField(
        label=_("Подтверждение пароля"),
        required=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
        labels = {
            "username": _("Имя пользователя"),
            "first_name": _("Имя"),
            "last_name": _("Фамилия"),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        existing = User.objects.filter(username=username)

        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError(
                _("Пользователь с таким именем уже существует")
            )

        return username

    def clean_password_confirm(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password_confirm")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Пароли не совпадают."))

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")

        if password1:
            user.set_password(password1)

        if commit:
            user.save()

        return user


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ["name"]
        labels = {"name": _("Имя")}
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ["name"]
        labels = {"name": _("Имя")}
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "status", "executor", "labels"]
        labels = {
            "name": _("Имя"),
            "description": _("Описание"),
            "status": _("Статус"),
            "executor": _("Исполнитель"),
            "labels": _("Метки"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "labels": forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "multiple": "multiple",
                },
            ),
        }
        help_texts = {
            "labels": _(
                "Удерживайте Ctrl (Cmd на Mac) для выбора нескольких меток"
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["executor"].queryset = User.objects.all()
