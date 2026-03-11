from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from task_manager.models import Task
from django.contrib import messages

User = get_user_model()


class TaskTests(TestCase):
    fixtures = ["users.json", "statuses.json", "labels.json", "tasks.json"]

    def test_tasks_list_unauthenticated_redirect(self):
        """список задач без авторизации — редирект"""
        response = self.client.get(reverse("tasks_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_tasks_list_authenticated(self):
        """список задач — залогинен"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("tasks_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовая задача")

    def test_task_create_get_authenticated(self):
        """форма создания задачи — залогинен"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_create"))
        self.assertEqual(response.status_code, 200)

    def test_task_create_unauthenticated(self):
        """создание задачи без авторизации"""
        response = self.client.get(reverse("task_create"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_task_update_other_allowed(self):
        """Обновление чужой задачи — разрешено"""
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(reverse("task_update", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_task_update_own_allowed(self):
        """Обновление своей задачи — разрешено"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_update", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_task_delete_other_forbidden(self):
        """чужая задача — сообщение + редирект"""
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.get(reverse("task_delete", args=[1]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("task_delete", args=[1]), data={"confirm": "yes"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(pk=1).exists())
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            "Задачу может удалить только её автор", str(messages_list[0])
        )

    def test_tasks_count(self):
        """проверка количества задач"""
        self.assertEqual(Task.objects.count(), 1)

    def test_task_detail_unauthenticated(self):
        """просмотр деталей без авторизации"""
        response = self.client.get(
            reverse("task_detail", args=[1]), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login")

    def test_task_update_post_own(self):
        """отправка изменений своей задачи"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("task_update", args=[1]),
            {
                "name": "Обновленная задача",
                "description": "Новое описание",
                "status": "2",
                "executor": "1",
            },
        )
        self.assertRedirects(response, reverse("tasks_list"))
        self.assertEqual(Task.objects.get(pk=1).name, "Обновленная задача")

    def test_task_delete_post_own(self):
        """удаление своей задачи"""
        self.client.login(username="testuser", password="testpass123")
        old_count = Task.objects.count()
        response = self.client.post(reverse("task_delete", args=[1]))
        self.assertRedirects(response, reverse("tasks_list"))
        self.assertEqual(Task.objects.count(), old_count - 1)

    def test_task_create_invalid_form(self):
        """создание задачи с невалидными данными не создает запись"""
        self.client.login(username="testuser", password="testpass123")
        old_count = Task.objects.count()
        response = self.client.post(
            reverse("task_create"),
            {
                "name": "",
                "description": "desc",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), old_count)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_task_detail_404_for_missing_task(self):
        """запрос несуществующей задачи дает 404"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_detail", args=[999]))
        self.assertEqual(response.status_code, 404)
