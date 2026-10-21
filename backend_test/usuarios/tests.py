from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group

class LoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
    def test_login(self):
        response = self.client.post('/accounts/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertIn('token', response_data)
        self.assertIn('refresh', response_data['token'])
        self.assertIn('access', response_data['token'])

        del response_data['token']

        expected_response = {
            'response': 'Login successful',
            'id': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'edad': self.user.edad,
            'sexo': self.user.sexo,
            'colegio': self.user.colegio,
            'celular': self.user.celular,
            'grado_escolar': self.user.grado_escolar,
            'email': self.user.email,
        }

        self.assertDictEqual(response_data, expected_response)

class RegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Group.objects.get_or_create(name='Administrador')
        Group.objects.get_or_create(name='Psicologo')

    def test_registration(self):
        response = self.client.post('/accounts/registeradmin/', {
            'username': '899561244',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User',
            'edad': 20,
            'sexo': 'M',
            'email': 'testuser@example.com',
            'role': 'Administrador'
        })
        self.assertEqual(response.status_code, 200)

        user = get_user_model().objects.get(username='899561244')
        self.assertTrue(user.groups.filter(name='Administrador').exists())

        expected_response = {
            'response': 'Registro de usuario exitoso',
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'edad': user.edad,
            'sexo': user.sexo,
            'email': user.email,
            'role': 'Administrador',
        }
        response_data = response.json()
        response_data.pop('token', None)

        self.assertDictEqual(response_data, expected_response)

    def test_registration_as_psicologo(self):
        response = self.client.post('/accounts/registeradmin/', {
            'username': '987654321',
            'password': 'testpassword',
            'first_name': 'Psico',
            'last_name': 'User',
            'edad': 25,
            'sexo': 'F',
            'email': 'psicologo@example.com',
            'role': 'Psicologo'
        })

        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(username='987654321')
        self.assertTrue(user.groups.filter(name='Psicologo').exists())
        self.assertFalse(user.groups.filter(name='Administrador').exists())
        self.assertEqual(response.json()['role'], 'Psicologo')