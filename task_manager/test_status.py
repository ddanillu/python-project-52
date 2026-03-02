from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Status, Task


class StatusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            first_name="Тест",
            last_name="Пользователь",
            password="testpass123",
        )
        cls.status1 = Status.objects.create(name="Новый")
        cls.status2 = Status.objects.create(name="В работе")

        cls.task1 = Task.objects.create(
            name="Тест", status=cls.status1, author=cls.user
        )

    def setUp(self):
        self.client.login(username="testuser", password="testpass123")

    def test_status_list(self):
        """список статусов"""
        response = self.client.get(reverse("statuses_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новый")

    def test_create_form(self):
        response = self.client.get(reverse("status_create"))
        self.assertEqual(response.status_code, 200)

    def test_status_create(self):
        response = self.client.post(
            reverse("status_create"),
            {
                "name": "test",
            },
        )

        self.assertRedirects(response, reverse("statuses_list"))
        self.assertTrue(Status.objects.filter(name="test").exists())

    def test_status_update(self):
        response = self.client.get(
            reverse("status_update", args=[self.status1.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_in_use_status(self):
        """Статус нельзя удалить, если связан с задачей"""
        response = self.client.post(
            reverse("status_delete", args=[self.status1.pk])
        )

        self.assertRedirects(response, reverse("statuses_list"))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("Статус не может быть удален", str(messages_list[0]))
        self.assertTrue(Status.objects.filter(pk=self.status1.pk).exists())

    def test_delete_is_not_used_status(self):
        """Статус можно удалить, если нет задач"""
        status3 = Status.objects.create(name="Свободный")

        response = self.client.post(reverse("status_delete", args=[status3.pk]))
        self.assertRedirects(response, reverse("statuses_list"))
        self.assertFalse(Status.objects.filter(pk=status3.pk).exists())
