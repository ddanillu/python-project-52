from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    DetailView,
)
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib import messages
from django_filters.views import FilterView
from .forms import RegisterForm, StatusForm, UserForm, LabelForm, TaskForm
from .models import Status, Task, Label
from .filters import TaskFilter


# Главная
class IndexView(TemplateView):
    template_name = "index.html"


# Список пользователей (без авторизации!)
class UserListView(ListView):
    model = User
    template_name = "users/users_list.html"
    context_object_name = "users"

    def get_regular_users(self):
        return (
            User.objects.filter(is_active=True)
            .exclude(is_staff=True, is_superuser=True)
            .order_by("username")
        )

    def get_queryset(self):
        return self.get_regular_users()


# Регистрация → редирект на login + сообщение об успехе
class RegisterView(SuccessMessageMixin, CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/form.html"
    success_url = reverse_lazy("login")
    success_message = _("Пользователь успешно зарегистрирован")


# Логин → редирект на главную + сообщение
class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        messages.success(self.request, _("Вы залогинены"))
        return super().form_valid(form)


# Выход + редирект на главную + сообщение
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        messages.success(self.request, _("Вы разлогинены"))
        return redirect(self.next_page)


# Редактирование (только своего юзера)
class UserUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = User
    form_class = UserForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users_list")
    success_message = _("Пользователь успешно изменен")

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj != self.request.user:
            messages.error(
                self.request,
                _("У вас нет прав для изменения пользователя"),
            )
            return redirect("users_list")
        return super().dispatch(request, *args, **kwargs)


# Удаление (только своего юзера)
class UserDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = User
    template_name = "users/user_delete.html"
    success_url = reverse_lazy("users_list")
    success_message = _("Пользователь успешно удален")

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj != self.request.user:
            messages.error(
                self.request,
                _("У вас нет прав для удаления другого пользователя"),
            )
            return redirect("users_list")

        if obj.tasks_authored.exists():
            messages.error(
                self.request,
                _("Нельзя удалить пользователя - у него есть задачи"),
            )
            return redirect("users_list")

        return super().dispatch(request, *args, **kwargs)


# Список статусов
class StatusesListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"


# Создание статуса (доступно только аунтифицированным пользователям)
class StatusCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses_list")

    def get_success_message(self, cleaned_data):
        return _("Статус успешно создан")


# Редактирование статуса (доступно только аунтифицированным пользователям)
class StatusUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses_list")

    def get_success_message(self, cleaned_data):
        return _("Статус успешно изменен")


# Удаление статуса (если статус не связан ни с одной задача)
class StatusDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Status
    template_name = "statuses/status_delete.html"
    success_url = reverse_lazy("statuses_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.task_set.exists():
            messages.error(
                self.request,
                _("Невозможно удалить статус, потому что он используется"),
            )
            return redirect("statuses_list")
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return _("Статус успешно удален")


# Список задач
class TaskListView(LoginRequiredMixin, FilterView):
    model = Task
    filterset_class = TaskFilter
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"


# Детали конкретной задачи
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"


# Создание задачи
class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return _("Задача успешно создана")


# Изменение задачи
class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks_list")

    def get_success_message(self, cleaned_data):
        return _("Задача успешно изменена")


# Удаление задачи (только автором)
class TaskDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Task
    template_name = "tasks/task_delete.html"
    success_url = reverse_lazy("tasks_list")

    def test_func(self):
        return self.get_object().author == self.request.user

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            messages.error(
                self.request, _("Задачу может удалить только ее автор")
            )
            return redirect("tasks_list")
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return _("Задача успешно удалена")


# Список меток
class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/labels_list.html"
    context_object_name = "labels"


# Создание метки
class LabelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/label_form.html"
    success_url = reverse_lazy("labels_list")

    def get_success_message(self, cleaned_data):
        return _("Метка успешно создана")


# Изменение метки
class LabelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/label_form.html"
    success_url = reverse_lazy("labels_list")

    def get_success_message(self, cleaned_data):
        return _("Метка успешно изменена")


# Удаление метки
class LabelDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Label
    template_name = "labels/label_delete.html"
    success_url = reverse_lazy("labels_list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.task_set.exists():
            messages.error(
                self.request,
                _("Невозможно удалить метку, потому что она используется"),
            )
            return redirect("labels_list")
        return super().dispatch(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return _("Метка успешно удалена")
