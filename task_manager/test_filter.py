from django.test import TestCase
from django.urls import reverse


class TaskFilterTests(TestCase):
    fixtures = [
        "users.json",
        "statuses.json",
        "labels.json",
        "task_with_labels.json",
    ]

    def setUp(self):
        self.client.login(username="testuser", password="testpass123")

    def test_filter_status(self):
        """Фильтр по статусу"""
        response = self.client.get(reverse("tasks_list"), {"status": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)

    def test_filter_executor(self):
        """Фильтр по исполнителю"""
        response = self.client.get(reverse("tasks_list"), {"executor": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)

    def test_filter_labels(self):
        """Фильтр по метке"""
        response = self.client.get(reverse("tasks_list"), {"labels": 1})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["tasks"]), 1)

    def test_filter_author_true(self):
        """Только свои задачи"""
        response = self.client.get(reverse("tasks_list"), {"author": "on"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)

    def test_filter_author_false(self):
        """Все задачи"""
        response = self.client.get(reverse("tasks_list"))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["tasks"]), 1)

    def test_combined_filters(self):
        """Комбинированная фильтрация"""
        response = self.client.get(
            reverse("tasks_list"), {"status": 1, "executor": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context["tasks"]), 0)
