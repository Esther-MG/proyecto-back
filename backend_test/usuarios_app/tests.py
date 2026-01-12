from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from usuarios.models import User  # Importa el modelo de usuario personalizado
from rest_framework import status
from usuarios_app.api.serializers import UserSerializer
import json
from usuarios_app.models import tutor, test, seccion, pregunta_sa, opcion_sa
from django.contrib.auth import get_user_model
class TestUserListAV(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='88222', password='Prueba')

    def test_get_user_list(self):
        self.client.login(username='88222', password='Prueba')
        response = self.client.get(reverse('usuarios-list'))
        self.assertEqual(response.status_code, 200)

        user_data = response.data[0]

        self.assertEqual(user_data['username'], '88222')
        self.assertEqual(user_data['email'], '')
        self.assertEqual(user_data['groups'], [])

class UsuarioDetailAVTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user1 = User.objects.create(username='testuser1', password='testpassword')
        self.test_user2 = User.objects.create(username='testuser2', password='testpassword')
        self.test_user3 = User.objects.create(username='testuser3', password='testpassword')

    def test_get_user(self):
        response = self.client.get(reverse('usuarios-detail', kwargs={'pk': self.test_user1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, UserSerializer(self.test_user1).data)

    def test_get_user_not_found(self):
        response = self.client.get(reverse('usuarios-detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_user(self):
        updated_data = {'username': 'updateduser', 'password': 'updatedpassword'}
        response = self.client.put(
            reverse('usuarios-detail', kwargs={'pk': self.test_user2.pk}),
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.test_user2.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user2.username, 'updateduser')
    def test_put_user_not_found(self):
        updated_data = {'username': 'updateduser', 'password': 'updatedpassword'}
        response = self.client.put(reverse('usuarios-detail', kwargs={'pk': 9999}), data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user(self):
        response = self.client.delete(reverse('usuarios-detail', kwargs={'pk': self.test_user3.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(pk=self.test_user3.pk)

    def test_delete_user_not_found(self):
        response = self.client.delete(reverse('usuarios-detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TutorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
    def test_tutor_create(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(f'/api/usuario/{self.user.pk}/tutor-create/', {
            'nombre': 'Test Tutor',
            'apellido': 'User',
            'ci': '123456789',
            'correo': 'tutor@example.com',
            'usuario_id': self.user.pk
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tutor.objects.count(), 1)
        self.assertEqual(tutor.objects.get().nombre, 'Test Tutor')
    def test_tutor_detail(self):
        self.client.login(username='testuser', password='testpassword')
        tutor_instance = tutor.objects.create(nombre='Test Tutor', apellido='User', ci='123456789', correo='tutor@example.com', usuario_id=self.user)
        response = self.client.get(f'/api/usuario/{self.user.pk}/tutor/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['nombre'], 'Test Tutor')

class TestDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test_instance = test.objects.create(nombre='Suficiencia Académica', instruccion='Instrucciones para el test')

    def test_test_detail(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/api/test/{self.test_instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['nombre'], 'Suficiencia Académica')
        self.assertEqual(response.data[0]['instruccion'], 'Instrucciones para el test')

class SeccionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test_instance = test.objects.create(nombre='Suficiencia Académica', instruccion='Instrucciones para el test')
    def test_seccion_create(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(f'/api/test/seccion/{self.test_instance.pk}/', {
            'nombre': 'Razonamiento Verbal',
            'instruccion': 'Instrucciones para la sección',
            'test_id': self.test_instance.pk
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(seccion.objects.count(), 1)
        self.assertEqual(seccion.objects.get(nombre='Razonamiento Verbal').nombre, 'Razonamiento Verbal')
    def test_seccion_detail(self):
        self.client.login(username='testuser', password='testpassword')
        seccion_instance = seccion.objects.create(nombre='Razonamiento Verbal', test_id=self.test_instance)
        response = self.client.get(f'/api/test/seccion/{seccion_instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['nombre'], 'Razonamiento Verbal')
        self.assertEqual(response.data[0]['test_id'], self.test_instance.id)

class PreguntaSATest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test_instance = test.objects.create(nombre='Suficiencia Académica', instruccion='Instrucciones para el test')
        self.seccion_instance = seccion.objects.create(nombre='Razonamiento Verbal', instruccion='Instruccion de la seccion', test_id=self.test_instance)

    def test_pregunta_sa_create(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(f'/api/test/seccion/pregunta/{self.seccion_instance.id}/', {
            'nro_pregunta': '1',
            'texto_pregunta': 'Pregunta Test',
            'seccion_id': self.seccion_instance.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(pregunta_sa.objects.count(), 1)
        self.assertEqual(pregunta_sa.objects.get(texto_pregunta='Pregunta Test').texto_pregunta, 'Pregunta Test')

    def test_pregunta_sa_detail(self):
        self.client.login(username='testuser', password='testpassword')
        pregunta_sa_instance = pregunta_sa.objects.create(nro_pregunta='1', texto_pregunta='Pregunta Test', seccion_id=self.seccion_instance)
        response = self.client.get(f'/api/test/seccion/pregunta/{pregunta_sa_instance.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['texto_pregunta'], 'Pregunta Test')

class OpcionSATest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test_instance = test.objects.create(nombre='Suficiencia Académica', instruccion='Instrucciones para el test')
        self.seccion_instance = seccion.objects.create(nombre='Razonamiento Verbal', instruccion='Instruccion de la seccion', test_id=self.test_instance)
        self.pregunta_sa_instance = pregunta_sa.objects.create(nro_pregunta='1', texto_pregunta='Pregunta Test', seccion_id=self.seccion_instance)

    def test_opcion_sa_create(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(f'/api/test/seccion/pregunta/opcion/{self.pregunta_sa_instance.id}/', {
            'inciso': 'A',
            'respuesta': 'Opcion Test',
            'valor': False,
            'pregunta_id': self.pregunta_sa_instance.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(opcion_sa.objects.count(), 1)
        self.assertEqual(opcion_sa.objects.get(inciso='A').inciso, 'A')

    def test_opcion_sa_detail(self):
        self.client.login(username='testuser', password='testpassword')
        opcion_sa_instance = opcion_sa.objects.create(inciso='A', respuesta='Opcion Test', valor=False, pregunta_id=self.pregunta_sa_instance)
        response = self.client.get(f'/api/test/seccion/pregunta/opcion/{opcion_sa_instance.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['inciso'], 'A')
