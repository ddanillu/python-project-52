from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from task_manager.models import Task, Status
from django.contrib import messages


User = get_user_model()


class TaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status1 = Status.objects.create(name="Новая")
        cls.status2 = Status.objects.create(name="Выполнена")
        cls.user1 = User.objects.create_user(
            username="author1", password="pass123"
        )
        cls.user2 = User.objects.create_user(
            username="executor1", password="pass123"
        )

        cls.task1 = Task.objects.create(
            name="Тестовая задача 1",
            description="Описание 1",
            status=cls.status1,
            author=cls.user1,
            executor=cls.user2,
        )

    def test_tasks_list_unauthenticated_redirect(self):
        """список задач без авторизации — редирект"""
        response = self.client.get(reverse("tasks_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_tasks_list_authenticated(self):
        """список задач — залогинен"""
        self.client.login(username="author1", password="pass123")
        response = self.client.get(reverse("tasks_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовая задача")

    def test_task_create_get_authenticated(self):
        """форма создания задачи — залогинен"""
        self.client.login(username="author1", password="pass123")
        response = self.client.get(reverse("task_create"))
        self.assertEqual(response.status_code, 200)

    def test_task_create_unauthenticated(self):
        """создание задачи без авторизации"""
        response = self.client.get(reverse("task_create"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_task_update_other_allowed(self):
        """Обновление чужой задачи — разрешено"""
        self.client.login(username="executor1", password="pass123")
        response = self.client.get(reverse("task_update", args=[self.task1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_task_update_own_allowed(self):
        """Обновление своей задачи — разрешено"""
        self.client.login(username="author1", password="pass123")
        response = self.client.get(reverse("task_update", args=[self.task1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_task_delete_other_forbidden(self):
        """чужая задача — сообщение + редирект"""
        self.client.login(username="executor1", password="pass123")
        response = self.client.get(reverse("task_delete", args=[self.task1.pk]))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn(
            "Задачу может удалить только ее автор", str(messages_list[0])
        )
        self.assertEqual(response.status_code, 302)

    def test_tasks_count(self):
        """проверка количества задач"""
        self.assertEqual(Task.objects.count(), 1)

    def test_task_detail_unauthenticated(self):
        """просмотр деталей без авторизации"""
        response = self.client.get(
            reverse("task_detail", args=[self.task1.pk]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_task_update_post_own(self):
        """отправка изменений своей задачи"""
        self.client.login(username="author1", password="pass123")
        response = self.client.post(
            reverse("task_update", args=[self.task1.pk]),
            {
                "name": "Обновленная задача",
                "description": "Новое описание",
                "status": self.status2.pk,
                "executor": self.user2.pk,
            },
        )
        self.assertRedirects(response, reverse("tasks_list"))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.name, "Обновленная задача")

    def test_task_delete_post_own(self):
        """удаление своей задачи"""
        self.client.login(username="author1", password="pass123")
        old_count = Task.objects.count()
        response = self.client.post(
            reverse("task_delete", args=[self.task1.pk])
        )
        self.assertRedirects(response, reverse("tasks_list"))
        self.assertEqual(Task.objects.count(), old_count - 1)
