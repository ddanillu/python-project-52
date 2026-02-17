from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='testuser',
            first_name='Тест',
            last_name='Пользователь',
            password='testpass123'
        )
        cls.user2 = User.objects.create_user(
            username='otheruser',
            first_name='Другой',
            last_name='Пользователь',
            password='otherpass123'
        )

    def test_users_list_unauthenticated(self):
        """список пользователей без входа"""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_register_get(self):
        """получаем форму регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_redirects_to_login(self):
        """редирект после регистрации"""
        response = self.client.post(reverse('register'), {
        'first_name': 'Test',
        'last_name': 'User', 
        'username': 'newuser',
        'password1': 'newpass123',
        'password2': 'newpass123'
    })
        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_update_own_allowed(self):
        """редактирование своего пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_update', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_user_update_other_forbidden(self):
        """редактирование чужого"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_update', args=[self.user2.pk]))
        self.assertEqual(response.status_code, 403)

    def test_user_delete_own_allowed(self):
        """удаление своего пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_delete', args=[self.user1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_user_delete_post_deletes_user(self):
        """удаление своего + редирект"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user_delete', args=[self.user1.pk]))
        self.assertRedirects(response, reverse('users'))
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())

    def test_login_post_redirects_to_tasks(self):
        """После логина — редирект на главную"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/')
