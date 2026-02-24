from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, StatusForm, UserForm
from .models import Status

# Главная
class IndexView(TemplateView):
    template_name = 'index.html'

# Список пользователей (без авторизации!)
class UserListView(ListView):
    model = User
    template_name = 'users/users_list.html'
    context_object_name = 'users'

    def get_regular_users(self):
        return User.objects.filter(
            is_active=True
        ).exclude(
            is_staff=True,
            is_superuser=True
        ).order_by('username')

    def get_queryset(self):
        return self.get_regular_users()


# Регистрация → редирект на login
class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('login')

# Логин → редирект на главную
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

# Выход + редирект на главную
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')
    
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)

# Редактирование (только своего юзера)
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user 

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj != self.request.user:
            messages.error(
                self.request, 
                "У вас нет прав для изменения другого пользователя."
            )
            return redirect('users_list')
        return super().dispatch(request, *args, **kwargs)

# Удаление (только своего юзера)
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'users/user_delete.html'
    success_url = reverse_lazy('users_list')

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user 
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj != self.request.user:
            messages.error(
                self.request,
                "У вас нет прав для удаления другого пользователя."
            )
            return redirect('users_list')  # ✅ Редирект + alert!
        return super().dispatch(request, *args, **kwargs)

# Список статусов
class StatusesListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = 'statuses/status_list.html'
    context_object_name = 'statuses'

# Создание статуса (доступно только аунтифицированным пользователям)
class StatusCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/status_form.html'
    success_url = reverse_lazy('statuses_list')

    def get_success_message(self, cleaned_data):
        return f"Статус '{cleaned_data['name']}' успешно создан"
    
# Редактирование статуса (доступно только аунтифицированным пользователям)
class StatusUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/status_form.html'
    success_url = reverse_lazy('statuses_list')

    def get_success_message(self, cleaned_data):
        return f"Статус '{cleaned_data['name']}' успешно изменен"
    
# Удаление статуса (если статус не связан ни с одной задача)
class StatusDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Status
    template_name = 'statuses/status_delete.html'
    success_url = reverse_lazy('statuses_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.task_set.exists():
            messages.error(
                self.request, 
                "Статус не может быть удален - связан с задачами"
            )
            return redirect('statuses_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_message(self, cleaned_data):
        return f"Статус '{self.object.name}' успешно удален"