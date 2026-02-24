from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Status


class StatusTests(TestCase):
    @classmethod
    def setUpTestData(cls): 
        cls.user = User.objects.create_user(
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
        cls.status1 = Status.objects.create(name='Новый')
        cls.status2 = Status.objects.create(name='В работе')

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

    def test_status_list(self):
        """список статусов"""
        response = self.client.get(reverse('statuses_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новый')

    def test_create_form(self):
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 200)

    def test_status_create(self):
        response = self.client.post(reverse('status_create'), {
            'name': 'test',
        })

        self.assertRedirects(response, reverse('statuses_list'))
        self.assertTrue(Status.objects.filter(name='test').exists())

    def test_status_update(self):
        response = self.client.get(reverse('status_update', args=[self.status1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_in_use_status(self):
        """Пока пропускаем — Task в следующем шаге"""
        pass

    def test_delete_is_not_used_status(self):
        """тоже нужна еще одна модель"""
        pass