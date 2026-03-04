from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from .models import Status


class StatusTests(TestCase):
    fixtures = ["users.json", "statuses.json", "tasks.json"]

    def setUp(self):
        self.client.login(username="testuser", password="testpass123")

    def test_status_list(self):
        """список статусов"""
        response = self.client.get(reverse("statuses_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новая")

    def test_create_form(self):
        """форма для создания"""
        response = self.client.get(reverse("status_create"))
        self.assertEqual(response.status_code, 200)

    def test_status_create(self):
        """создание статуса"""
        response = self.client.post(
            reverse("status_create"),
            {
                "name": "test",
            },
        )

        self.assertRedirects(response, reverse("statuses_list"))
        self.assertTrue(Status.objects.filter(name="test").exists())

    def test_status_update(self):
        """обновление статуса"""
        response = self.client.get(reverse("status_update", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_delete_in_use_status(self):
        """Статус нельзя удалить, если он связан с задачей"""
        response = self.client.post(reverse("status_delete", args=[1]))

        self.assertRedirects(response, reverse("statuses_list"))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertIn("Невозможно удалить статус", str(messages_list[0]))
        self.assertTrue(Status.objects.filter(pk=1).exists())

    def test_delete_is_not_used_status(self):
        """Статус можно удалить, если нет задач"""
        response = self.client.post(reverse("status_delete", args=[2]))
        self.assertRedirects(response, reverse("statuses_list"))
        self.assertFalse(Status.objects.filter(pk=2).exists())
