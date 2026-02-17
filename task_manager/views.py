from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from django.core.exceptions import PermissionDenied

# Главная
class IndexView(TemplateView):
    template_name = 'index.html'

# Список пользователей (без авторизации!)
class UserListView(ListView):
    model = User
    template_name = 'users_list.html'
    context_object_name = 'users'
    paginate_by = 10

# Регистрация → редирект на login
class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'form.html'
    success_url = '/login/'

# Логин → редирект на главную
class CustomLoginView(LoginView):
    template_name = 'login.html'

# Логаут → главная
class CustomLogoutView(LogoutView):
    next_page = '/'

# Редактирование (только своего юзера)
class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = RegisterForm
    template_name = 'form.html'
    success_url = '/users/'

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user
    
    def get_permission_denied_message(self):
        return "У вас нет прав для изменения другого пользователя."

# Удаление (только своего юзера)
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'user_delete.html'
    success_url = '/users/'

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user
    
    def get_permission_denied_message(self):
        return "У вас нет прав для удаления другого пользователя."
