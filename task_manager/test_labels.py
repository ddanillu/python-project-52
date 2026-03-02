from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from task_manager.models import Label, Task, Status


class LabelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            first_name="Тест",
            last_name="Пользователь",
            password="testpass123",
        )
        cls.status = Status.objects.create(name="Test Status")
        cls.label1 = Label.objects.create(name="bug")
        cls.label2 = Label.objects.create(name="feature")
        cls.task = Task.objects.create(
            name="Test task with label",
            description="Test",
            status=cls.status,
            author=cls.user,
        )
        cls.task.labels.add(cls.label1)

    def setUp(self):
        self.client.login(username="testuser", password="testpass123")

    def test_labels_list(self):
        """список меток"""
        response = self.client.get(reverse("labels_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bug")

    def test_labels_create_get(self):
        """форма создания метки"""
        response = self.client.get(reverse("label_create"))
        self.assertEqual(response.status_code, 200)

    def test_labels_create_post(self):
        """создание метки"""
        response = self.client.post(
            reverse("label_create"),
            {"name": "test-label"},
        )
        self.assertRedirects(response, reverse("labels_list"))
        self.assertTrue(Label.objects.filter(name="test-label").exists())

    def test_label_update_get(self):
        """форма редактирования"""
        response = self.client.get(
            reverse("label_update", args=[self.label1.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_label_update_post(self):
        """обновление метки"""
        response = self.client.post(
            reverse("label_update", args=[self.label1.pk]),
            {"name": "updated-bug"},
        )
        self.assertRedirects(response, reverse("labels_list"))
        self.label1.refresh_from_db()
        self.assertEqual(self.label1.name, "updated-bug")

    def test_label_delete_get(self):
        """форма удаления"""
        response = self.client.get(
            reverse("label_delete", args=[self.label2.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_label_delete_free(self):
        """удаление свободной метки"""
        response = self.client.post(
            reverse("label_delete", args=[self.label2.pk])
        )
        self.assertRedirects(response, reverse("labels_list"))
        self.assertFalse(Label.objects.filter(pk=self.label2.pk).exists())

    def test_label_delete_protected(self):
        """нельзя удалить связанную метку"""
        response = self.client.post(
            reverse("label_delete", args=[self.label1.pk])
        )
        self.assertRedirects(response, reverse("labels_list"))
        self.assertTrue(Label.objects.filter(pk=self.label1.pk).exists())
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn("Невозможно удалить метку", str(messages_list[0]))
