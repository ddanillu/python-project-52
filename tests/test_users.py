from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from task_manager.forms import UserForm, RegisterForm


class UserTests(TestCase):
    fixtures = ["users.json"]

    def test_users_list_unauthenticated(self):
        """список пользователей без входа"""
        response = self.client.get(reverse("users_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")

    def test_register_get(self):
        """получаем форму регистрации"""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_post_redirects_to_login(self):
        """редирект после регистрации"""
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Test",
                "last_name": "User",
                "username": "newuser",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_update_own_allowed(self):
        """редактирование своего пользователя"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("user_update", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_user_update_other_forbidden(self):
        """редактирование чужого"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("user_update", args=[2]))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("У вас нет прав", str(messages_list[0]))

    def test_user_delete_own_allowed(self):
        """удаление своего пользователя"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("user_delete", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_user_delete_post_deletes_user(self):
        """удаление своего + редирект"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("user_delete", args=[1]))
        self.assertRedirects(response, reverse("users_list"))
        self.assertFalse(User.objects.filter(pk=1).exists())

    def test_login_post_redirects_to_tasks(self):
        """После логина — редирект на главную"""
        self.form_data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(
            reverse("login"), self.form_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Добро")


class UserFormTests(TestCase):
    fixtures = ["users.json"]

    def test_user_form_change_password(self):
        """Сохранение нового пароля через форму"""
        user = User.objects.first()
        form = UserForm(
            instance=user,
            data={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password1": "newstrongpass123",
                "password2": "newstrongpass123",
            },
        )
        self.assertTrue(form.is_valid())
        updated = form.save()
        self.assertTrue(updated.check_password("newstrongpass123"))


class RegisterFormTests(TestCase):
    fixtures = ["users.json"]

    def test_register_form_duplicate_username(self):
        """RegisterForm: дублирующийся username не проходит"""
        existing = User.objects.first()
        form = RegisterForm(
            data={
                "first_name": "New",
                "last_name": "Name",
                "username": existing.username,
                "password1": "somepass123",
                "password2": "somepass123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_register_form_password_mismatch(self):
        """RegisterForm: пароли не совпадают"""
        form = RegisterForm(
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "new-user-xyz",
                "password1": "pass1",
                "password2": "pass2",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class UserMessagesTests(TestCase):
    def test_register_success_message_and_redirect(self):
        """После регистрации: редирект на /login/ и сообщение"""
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Test",
                "last_name": "User",
                "username": "newuser2",
                "password1": "newpass123",
                "password2": "newpass123",
            },
            follow=True,
        )
        self.assertEqual(response.resolver_match.view_name, "login")
        self.assertContains(response, "Пользователь успешно зарегистрирован")


class IndexTests(TestCase):
    def test_index_page_renders(self):
        """Главная страница отдается и содержит приветствие"""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Менеджер задач")
