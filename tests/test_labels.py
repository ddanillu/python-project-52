from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from task_manager.models import Label


class LabelTests(TestCase):
    fixtures = [
        "users.json",
        "statuses.json",
        "labels.json",
        "task_with_labels.json",
    ]

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
        response = self.client.get(reverse("label_update", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_label_update_post(self):
        """обновление метки"""
        response = self.client.post(
            reverse("label_update", args=[1]),
            {"name": "updated-bug"},
        )
        self.assertRedirects(response, reverse("labels_list"))
        self.assertEqual(Label.objects.get(pk=1).name, "updated-bug")

    def test_label_create_duplicate_name_invalid(self):
        """нельзя создать метку с уже существующим именем"""
        response = self.client.post(
            reverse("label_create"),
            {"name": "bug"},
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_label_delete_get(self):
        """форма удаления"""
        response = self.client.get(reverse("label_delete", args=[2]))
        self.assertEqual(response.status_code, 200)

    def test_label_delete_free(self):
        """удаление свободной метки"""
        response = self.client.post(reverse("label_delete", args=[2]))
        self.assertRedirects(response, reverse("labels_list"))
        self.assertFalse(Label.objects.filter(pk=2).exists())

    def test_label_delete_protected(self):
        """нельзя удалить связанную метку"""
        response = self.client.post(reverse("label_delete", args=[1]))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("label_delete", args=[1]), data={"confirm": "yes"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Label.objects.filter(pk=1).exists())
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn("Невозможно удалить метку", str(messages_list[0]))
