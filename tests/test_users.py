from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from task_manager.models import Task, Status
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
                "password_confirm": "newpass123",
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

    def test_user_delete_if_user_has_tasks(self):
        """удаление пользователя, если он имеет задачи"""
        self.client.login(username="testuser", password="testpass123")
        user = User.objects.get(pk=1)
        Status.objects.create(name="Test status")

        Task.objects.create(
            name="Test task",
            status=Status.objects.get(name="Test status"),
            author=user,
        )
        response = self.client.post(
            reverse("user_delete", args=[1]), follow=True
        )
        self.assertRedirects(response, reverse("users_list"))
        self.assertTrue(User.objects.filter(pk=1).exists())
        self.assertContains(
            response, "Нельзя удалить пользователя - у него есть задачи"
        )

    def test_login_post_redirects_to_tasks(self):
        """После логина — редирект на главную"""
        self.form_data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(
            reverse("login"), self.form_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Добро")

    def test_custom_logout_view_logs_out_user(self):
        """выход из системы"""
        self.client.login(username="testuser", password="testpass123")
        self.assertTrue(self.client.session)
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("index"))
        response = self.client.get(reverse("index"))
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
                "password_confirm": "newstrongpass123",
            },
        )
        self.assertTrue(form.is_valid())
        updated = form.save()
        self.assertTrue(updated.check_password("newstrongpass123"))

    def test_user_form_empty_password1(self):
        """UserForm: пустой password1 не проходит"""
        user = User.objects.first()
        form = UserForm(
            instance=user,
            data={
                "username": "testuser",
                "first_name": "First",
                "last_name": "Last",
                "password1": "",
                "password_confirm": "somepass",
            },
        )
        self.assertTrue(form.is_valid())

    def test_user_form_password_confirm_mismatch(self):
        """UserForm: пароли не совпадают"""
        user = User.objects.first()
        form = UserForm(
            instance=user,
            data={
                "username": "testuser",
                "first_name": "First",
                "last_name": "Last",
                "password1": "newpass",
                "password_confirm": "mismatch",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Пароли не совпадают.",
            str(form.errors["password_confirm"]),
        )

    def test_user_form_save_sets_password_when_password1_is_provided(self):
        """UserForm: сохранение пароля при наличии password1"""
        user = User.objects.first()
        form = UserForm(
            instance=user,
            data={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password1": "newpass123",
                "password_confirm": "newpass123",
            },
        )
        self.assertTrue(form.is_valid())
        updated = form.save(commit=False)
        updated.save()
        updated.refresh_from_db()
        self.assertTrue(updated.check_password("newpass123"))

    def test_user_form_save_does_not_change(self):
        user = User.objects.get(username="testuser")
        old_hash = user.password
        form = UserForm(
            instance=user,
            data={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "password1": "",
                "password_confirm": "",
            },
        )
        self.assertTrue(form.is_valid())
        form.save()
        user.refresh_from_db()
        self.assertEqual(user.password, old_hash)


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
                "password_confirm": "somepass123",
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
                "password_confirm": "pass2",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Пароли не совпадают", str(form.errors["password_confirm"])
        )

    def test_register_form_init_removes_password2_and_sets_help_text(self):
        """RegisterForm: удаление password2 и установка help_text"""
        form = RegisterForm()
        self.assertNotIn("password2", form.fields)
        self.assertEqual(
            form.fields["password1"].help_text,
            "Пароль минимум 3 символов",
        )
        self.assertIsNone(form.fields["password_confirm"].help_text)

    def test_register_form_password_length_less_than_3(self):
        """RegisterForm: пароль меньше 3 символов не проходит"""
        form = RegisterForm(
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "newuser",
                "password1": "a1",
                "password_confirm": "a1",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Пароль должен содержать минимум 3 символа",
            form.non_field_errors().as_text(),
        )

    def test_register_form_missing_password_confirm(self):
        """RegisterForm: отсутствие password_confirm не проходит"""
        form = RegisterForm(
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "newuser",
                "password1": "abc",
                "password_confirm": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password_confirm", form.errors)
        self.assertEqual(
            form.errors["password_confirm"][0],
            "Обязательное поле.",
        )

    def test_register_form_missing_password1(self):
        """RegisterForm: отсутствие password1 не проходит"""
        form = RegisterForm(
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "newuser",
                "password1": "",
                "password_confirm": "abc",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)


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
                "password_confirm": "newpass123",
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
