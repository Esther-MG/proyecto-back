from usuarios_app.models import (usuario, tipo_usuario, tutor, test, seccion, pregunta_sa, opcion_sa, encuesta,
respuesta1, pregunta_ipp, opcion_ipp, respuesta2, pregunta_hspq, opcion_hspq, respuesta3)
from usuarios.models import User
from django.contrib.auth.models import Group
from usuarios_app.api.serializers import (UsuarioSerializer, TipoUsuarioSerializer, TutorSerializer,
TestSerializer, SeccionSerializer, PreguntaSASerializer, OpcionSASerializer, UserSerializer,GroupsSerializer,
UserGroupSerializer, EncuestaSerializer, Respuesta1Serializer, PreguntaIPPSerializer, OpcionIPPSerializer, Respuesta2Serializer,
PreguntaHSPQSerializer, OpcionHSPQSerializer, Respuesta3Serializer)
from rest_framework.response import Response
#from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets, generics,mixins
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.forms.models import model_to_dict


class TipoUsuarioAV(APIView):
    def get(self, request):
        TipoUsuario = tipo_usuario.objects.all()
        serializer = TipoUsuarioSerializer(TipoUsuario, many=True)
        return Response(serializer.data)
    
class GroupUsuarioAV(APIView):
    def get(self, request):
        Groups = Group.objects.all()
        serializer = GroupsSerializer(Groups, many=True)
        return Response(serializer.data)
    
# class UsuarioListVS(viewsets.ViewSet):
#     def list(self, request):
#         queryset = usuario.objects.all()
#         serializer = UsuarioSerializer(queryset, many=True)
#         return Response(serializer.data)
#     def retrieve(self, request,pk=None):
#         queryset = usuario.objects.all()
#         usuarioList = get_object_or_404(queryset, pk=pk)
#         serializer = UsuarioSerializer(usuarioList)
#         return Response(serializer.data)     

class UserListAV(APIView):
    def get(self, request):
        Usuario = User.objects.all()
        serializer = UserSerializer(Usuario, many=True)
        return Response(serializer.data)

class UserGroupView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        groups = [group.name for group in user.groups.all()]
        return Response({'groups': groups})
        
class UsuarioDetailAV(APIView):
    def get(self, request,pk):
        try:
            Usuario = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(Usuario)
        return Response(serializer.data)
    def put(self,request,pk):
        try:
            Usuario = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(Usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        try:
            Usuario = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'Error': 'Usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
        Usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TutorListAV(generics.RetrieveUpdateDestroyAPIView):
    queryset = tutor.objects.all()
    serializer_class = TutorSerializer
    
class EncuestaAV(generics.ListCreateAPIView):
    serializer_class = EncuestaSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return encuesta.objects.filter(usuario_id=pk)
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        idusuario = User.objects.get(pk=pk)
        serializer.save(usuario_id=idusuario)

class TutorCreate(generics.CreateAPIView):
    serializer_class = TutorSerializer
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        idusuario = User.objects.get(pk=pk)
        serializer.save(usuario_id=idusuario)

class TutorDetailAV(generics.ListCreateAPIView):
    serializer_class = TutorSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return tutor.objects.filter(usuario_id=pk)

class TestView(APIView):
    def get(self, request):
        Test = test.objects.all()
        serializer = TestSerializer(Test, many=True)
        return Response(serializer.data)
class TestDetailAV(generics.ListCreateAPIView):
    serializer_class = TestSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return test.objects.filter(id=pk)

class SeccionView(APIView):
    def get(self, request):
        Seccion = seccion.objects.all()
        serializer = SeccionSerializer(Seccion, many=True)
        return Response(serializer.data)
    
class SeccionDetailAV(generics.ListCreateAPIView):
    serializer_class = SeccionSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return seccion.objects.filter(test_id=pk)

class PreguntaView(APIView):
    def get(self, request):
        Pregunta = pregunta_sa.objects.all()
        serializer = PreguntaSASerializer(Pregunta, many=True)
        return Response(serializer.data)
    
class PreguntaSADetailAV(generics.ListCreateAPIView):
    serializer_class = PreguntaSASerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return pregunta_sa.objects.filter(seccion_id=pk).order_by('id')

class OpcionView(APIView):
    def get(self, request):
        Opcion = opcion_sa.objects.all()
        serializer = OpcionSASerializer(Opcion, many=True)
        return Response(serializer.data)
    
class OpcionSADetailAV(generics.ListCreateAPIView):
    serializer_class = OpcionSASerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return opcion_sa.objects.filter(pregunta_id=pk)

class Respuesta1AV(generics.CreateAPIView):
    serializer_class = Respuesta1Serializer
    #permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            usuario = self.request.user
            opcion_pk = self.kwargs.get('opcion_pk')
            idOpcion = get_object_or_404(opcion_sa, pk=opcion_pk)
            serializer.save(usuario_id=usuario, opcion_id=idOpcion)
        else:
            raise PermissionDenied("Usuario no autenticado")

class Respuesta1View(generics.ListAPIView):
    serializer_class = Respuesta1Serializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return respuesta1.objects.filter(usuario_id=pk)

def calculate_correct_answers_seccion1(correct_answers):
    if 0 <= correct_answers <= 9:
        return 1
    elif 10 == correct_answers:
        return 2
    elif 11 == correct_answers:
        return 4
    elif 12 == correct_answers:
        return 5
    elif 13 <= correct_answers <= 14:
        return 10
    elif 15 == correct_answers:
        return 15
    elif 16 == correct_answers:
        return 20
    elif 17 == correct_answers:
        return 25
    elif 18 == correct_answers:
        return 30
    elif 19 == correct_answers:
        return 35
    elif 20 == correct_answers:
        return 40
    elif 21 == correct_answers:
        return 50
    elif 22 == correct_answers:
        return 55
    elif 23 == correct_answers:
        return 65
    elif 24 == correct_answers:
        return 70
    elif 25 == correct_answers:
        return 75
    elif 26 == correct_answers:
        return 80
    elif 27 <= correct_answers <= 28:
        return 85
    elif 29 <= correct_answers <= 31:
        return 90
    elif 32 == correct_answers:
        return 96
    elif 33 == correct_answers:
        return 97
    elif 34 == correct_answers:
        return 98
    elif 35 <= correct_answers:
        return 99

def calculate_correct_answers_seccion2(correct_answers):
    if 0 <= correct_answers <= 4:
        return 1
    elif 5 == correct_answers:
        return 3
    elif 6 == correct_answers:
        return 5
    elif 7 <= correct_answers <= 8:
        return 10
    elif 9 == correct_answers:
        return 15
    elif 10 == correct_answers:
        return 20
    elif 11 == correct_answers:
        return 25
    elif 12 == correct_answers:
        return 35
    elif 13 == correct_answers:
        return 40
    elif 14 == correct_answers:
        return 45
    elif 15 == correct_answers:
        return 55
    elif 16 == correct_answers:
        return 60
    elif 17 == correct_answers:
        return 70
    elif 18 == correct_answers:
        return 75
    elif 19 == correct_answers:
        return 80
    elif 20 <= correct_answers <= 21:
        return 85
    elif 22 <= correct_answers <= 26:
        return 90
    elif 27 <= correct_answers <= 28:
        return 95
    elif 29 == correct_answers:
        return 97
    elif 30 <= correct_answers <= 31:
        return 98
    elif 32 <= correct_answers:
        return 99

def calculate_correct_answers_seccion3(correct_answers):
    if 0 <= correct_answers <= 7:
        return 1
    elif 8 == correct_answers:
        return 2
    elif 9 == correct_answers:
        return 3
    elif 10 == correct_answers:
        return 4
    elif 11 <= correct_answers <= 12:
        return 10
    elif 13 <= correct_answers <= 14:
        return 15
    elif 15 == correct_answers:
        return 20
    elif 16 == correct_answers:
        return 25
    elif 17 == correct_answers:
        return 30
    elif 18 == correct_answers:
        return 35
    elif 19 <= correct_answers <= 20:
        return 40
    elif 21 == correct_answers:
        return 45
    elif 22 <= correct_answers <= 23:
        return 55
    elif 24 == correct_answers:
        return 60
    elif 25 == correct_answers:
        return 70
    elif 26 <= correct_answers <= 27:
        return 75
    elif 28 == correct_answers:
        return 80
    elif 29 <= correct_answers <= 30:
        return 85
    elif 31 <= correct_answers <= 33:
        return 90
    elif 34 == correct_answers:
        return 95
    elif 35 == correct_answers:
        return 96
    elif 36 <= correct_answers:
        return 99

def calculate_correct_answers_seccion4(correct_answers):
    if 0 <= correct_answers <= 13:
        return 1
    elif 14 <= correct_answers <= 15:
        return 2
    elif 16 == correct_answers:
        return 3
    elif 17 == correct_answers:
        return 4
    elif 18 <= correct_answers <= 20:
        return 5
    elif 21 == correct_answers:
        return 10
    elif 22 == correct_answers:
        return 15
    elif 23 == correct_answers:
        return 20
    elif 24 <= correct_answers <= 25:
        return 25
    elif 26 == correct_answers:
        return 30
    elif 27 == correct_answers:
        return 35
    elif 28 <= correct_answers <= 30:
        return 40
    elif 31 == correct_answers:
        return 45
    elif 32 <= correct_answers <= 36:
        return 55
    elif 37 == correct_answers:
        return 60
    elif 38 <= correct_answers <= 39:
        return 70
    elif 40 <= correct_answers <= 42:
        return 75
    elif 43 <= correct_answers <= 44:
        return 80
    elif 45 <= correct_answers <= 46:
        return 85
    elif 47 <= correct_answers <= 49:
        return 90
    elif 50 == correct_answers:
        return 95
    elif 51 == correct_answers:
        return 97
    elif 52 <= correct_answers <= 53:
        return 98
    elif 54 <= correct_answers:
        return 99

def calculate_correct_answers_seccion5(correct_answers):
    if 0 <= correct_answers <= 4:
        return 1
    elif 5 == correct_answers:
        return 2
    elif 6 == correct_answers:
        return 3
    elif 7 == correct_answers:
        return 4
    elif 8 <= correct_answers <= 11:
        return 5
    elif 12 <= correct_answers <= 13:
        return 10
    elif 14 == correct_answers:
        return 15
    elif 15 <= correct_answers <= 16:
        return 20
    elif 17 == correct_answers:
        return 25
    elif 18 == correct_answers:
        return 30
    elif 19 <= correct_answers <= 20:
        return 35
    elif 21 <= correct_answers <= 23:
        return 40
    elif 24 == correct_answers:
        return 45
    elif 25 == correct_answers:
        return 50
    elif 26 <= correct_answers <= 27:
        return 55
    elif 28 == correct_answers:
        return 60
    elif 29 == correct_answers:
        return 65
    elif 30 <= correct_answers <= 31:
        return 70
    elif 32 <= correct_answers <= 33:
        return 75
    elif 34 <= correct_answers <= 35:
        return 80
    elif 36 <= correct_answers <= 37:
        return 85
    elif 38 <= correct_answers <= 39:
        return 90
    elif 40 == correct_answers:
        return 95
    elif 41 <= correct_answers <= 43:
        return 96
    elif 44 == correct_answers:
        return 97
    elif 45 <= correct_answers <= 46:
        return 98
    elif 47 <= correct_answers:
        return 99

def calculate_correct_answers_seccion6(correct_answers):
    if 0 <= correct_answers <= 13:
        return 1
    elif 14 <= correct_answers <= 15:
        return 2
    elif 16 == correct_answers:
        return 3
    elif 17 == correct_answers:
        return 4
    elif 18 <= correct_answers <= 19:
        return 5
    elif 20 <= correct_answers <= 21:
        return 10
    elif 22 <= correct_answers <= 24:
        return 15
    elif 25 == correct_answers:
        return 20
    elif 26 == correct_answers:
        return 25
    elif 27 == correct_answers:
        return 30
    elif 28 <= correct_answers <= 29:
        return 40
    elif 30 == correct_answers:
        return 45
    elif 31 <= correct_answers <= 32:
        return 55
    elif 33 == correct_answers:
        return 60
    elif 34 == correct_answers:
        return 70
    elif 35 == correct_answers:
        return 80
    elif 36 == correct_answers:
        return 85
    elif 37 == correct_answers:
        return 90
    elif 38 == correct_answers:
        return 96
    elif 39 == correct_answers:
        return 98
    elif 40 <= correct_answers:
        return 99

def calculate_correct_answers_seccion7(correct_answers):
    if 0 <= correct_answers <= 31:
        return 1
    elif 32 <= correct_answers <= 36:
        return 2
    elif 37 == correct_answers:
        return 3
    elif 38 == correct_answers:
        return 4
    elif 39 <= correct_answers <= 41:
        return 5
    elif 42 <= correct_answers <= 44:
        return 10
    elif 45 == correct_answers:
        return 15
    elif 46 <= correct_answers <= 49:
        return 20
    elif 50 <= correct_answers <= 51:
        return 25
    elif 52 == correct_answers:
        return 30
    elif 53 == correct_answers:
        return 35
    elif 54 <= correct_answers <= 55:
        return 40
    elif 56 == correct_answers:
        return 45
    elif 57 <= correct_answers <= 60:
        return 55
    elif 61 == correct_answers:
        return 60
    elif 62 == correct_answers:
        return 65
    elif 63 <= correct_answers <= 64:
        return 70
    elif 65 <= correct_answers <= 67:
        return 75
    elif 68 <= correct_answers <= 69:
        return 80
    elif 70 <= correct_answers <= 74:
        return 85
    elif 75 <= correct_answers <= 82:
        return 90
    elif 83 <= correct_answers <= 84:
        return 95
    elif 85 <= correct_answers <= 86:
        return 96
    elif 87 <= correct_answers <= 89:
        return 97
    elif 90 <= correct_answers <= 93:
        return 98
    elif 94 <= correct_answers:
        return 99

calculate_correct_answers_functions = {
    1: calculate_correct_answers_seccion1,
    2: calculate_correct_answers_seccion2,
    3: calculate_correct_answers_seccion3,
    4: calculate_correct_answers_seccion4,
    5: calculate_correct_answers_seccion5,
    6: calculate_correct_answers_seccion6,
    7: calculate_correct_answers_seccion7,
}
class TestResultsView(APIView):
    def get(self, request, user_id, apartado_id):
        user_answers = respuesta1.objects.filter(usuario_id=user_id, id_apartado=apartado_id)
        correct_answers = 0
        for answer in user_answers:
            if answer.opcion_id.valor:
                correct_answers += 1

        calculate_correct_answers_function = calculate_correct_answers_functions.get(apartado_id)

        if calculate_correct_answers_function is not None:
            correct_answers = calculate_correct_answers_function(correct_answers)

        return Response({'correct_answers': correct_answers})

class UserTestResultsTotal(APIView):
    def get(self, request, user_id):
        # Obtén todas las respuestas para el test con id 1
        user_answers = respuesta1.objects.filter(usuario_id=user_id, id_test=1)

        # Calcula el puntaje total
        total_score = user_answers.aggregate(Sum('valor'))['valor__sum']

        # Inicializa una lista para almacenar los resultados
        resultados = []

        # Para cada sección, calcula el puntaje total y el puntaje convertido
        for section in seccion.objects.filter(test_id=1):
            section_answers = user_answers.filter(id_apartado=section.id)
            section_score = section_answers.aggregate(Sum('valor'))['valor__sum']

            calculate_correct_answers_function = calculate_correct_answers_functions.get(section.id)

            if calculate_correct_answers_function is not None:
                converted_score = calculate_correct_answers_function(section_score)
            else:
                converted_score = section_score

            # Agrega los resultados a la lista
            resultados.append({
                'test': 1,
                'seccion': section.id,
                'puntaje_total': section_score,
                'conversion': converted_score
            })

        # Devuelve los resultados en la respuesta
        return Response(resultados)
class Conversion(APIView):
    def get(self, request, user_id):
        # Obtén todas las respuestas para el test con id 1
        user_answers = respuesta1.objects.filter(usuario_id=user_id, id_test=1)

        # Inicializa una lista para almacenar los resultados
        resultados = []

        # Para cada sección, calcula el puntaje total y el puntaje convertido
        for section in seccion.objects.filter(test_id=1):
            section_answers = user_answers.filter(id_apartado=section.id)
            section_score = section_answers.aggregate(Sum('valor'))['valor__sum']

            calculate_correct_answers_function = calculate_correct_answers_functions.get(section.id)

            if calculate_correct_answers_function is not None:
                converted_score = calculate_correct_answers_function(section_score)
            else:
                converted_score = section_score

            # Agrega los resultados a la lista
            resultados.append({
                'conversion': converted_score
            })

        # Devuelve los resultados en la respuesta
        return Response(resultados)
class UserSectionResponsesView(generics.ListAPIView):
    serializer_class = Respuesta1Serializer
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        section_id = self.kwargs['section_id']
        return respuesta1.objects.filter(usuario_id=user_id, id_apartado=section_id)

class PreguntaIppView(APIView):
    def get(self, request):
        Pregunta = pregunta_ipp.objects.all()
        serializer = PreguntaIPPSerializer(Pregunta, many=True)
        return Response(serializer.data)

class PreguntaIPPDetails(generics.ListCreateAPIView):
    serializer_class = PreguntaIPPSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return pregunta_ipp.objects.filter(test_id=pk).order_by('id')

class OpcionIppView(APIView):
    def get(self, request):
        Opcion = opcion_ipp.objects.all()
        serializer = OpcionIPPSerializer(Opcion, many=True)
        return Response(serializer.data)

class Respuesta2AV(generics.CreateAPIView):
    serializer_class = Respuesta2Serializer
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            usuario = self.request.user
            pregunta_pk = self.kwargs.get('pregunta_pk')
            opcion_pk = self.kwargs.get('opcion_pk')
            idOpcion = get_object_or_404(opcion_ipp, pk=opcion_pk)
            idPregunta = get_object_or_404(pregunta_ipp, pk=pregunta_pk)
            serializer.save(usuario_id=usuario, pregunta_id=idPregunta, opcion_id=idOpcion)
        else:
            raise PermissionDenied("Usuario no autenticado")

class Respuesta2View(generics.ListAPIView):
    serializer_class = Respuesta2Serializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return respuesta2.objects.filter(usuario_id=pk)

class UserSectionSumView(APIView):
    def get(self, request, user_id):
        user_answers = respuesta2.objects.filter(usuario_id=user_id)
        sections = set(user_answers.values_list('pregunta_id__seccion', flat=True))
        categories = sorted(set(user_answers.values_list('categoria', flat=True)), key=lambda x: x != 'AC')
        data = []
        for section in sections:
            section_data = {'section': section}
            for category in categories:
                category_sum = user_answers.filter(pregunta_id__seccion=section, categoria=category).aggregate(Sum('valor'))['valor__sum']
                converted_score = convert_score(category_sum, category, section)
                section_data[category] = converted_score
            data.append(section_data)
        return Response(data)

def convert_score(score, category, section):
    score_map = {
        'AC': {
            1: [1, 20, 35, 45, 55, 70, 75, 85, 90, 95, 97, 99],
            2: [1, 20, 30, 40, 55, 65, 70, 80, 90, 95, 97, 99],
            3: [1, 25, 35, 45, 50, 60, 65, 75, 80, 85, 90, 95, 98],
            4: [1, 20, 35, 45, 55, 70, 80, 85, 95, 96, 98, 99],
            5: [1, 20, 30, 40, 50, 60, 65, 75, 80, 85, 90, 95, 98],
            6: [1, 20, 30, 35, 45, 55, 65, 75, 80, 85, 90, 96, 99],
            7: [1, 25, 40, 50, 60, 70, 75, 85, 90, 95, 98, 99],
            8: [1, 30, 40, 50, 55, 65, 70, 75, 80, 85, 90, 95, 98],
            9: [1, 10, 25, 35, 50, 60, 75, 85, 90, 95, 98, 99],
            10: [1, 25, 35, 50, 60, 70, 75, 85, 90, 90, 95, 98, 99],
            11: [1, 25, 30, 40, 45, 55, 60, 65, 70, 75, 85, 90, 98],
            12: [1, 45, 60, 70, 75, 80, 90, 95, 96, 98, 99],
            13: [1, 25, 35, 40, 50, 55, 65, 70, 75, 80, 90, 95, 98],
            14: [1, 15, 30, 40, 50, 60, 65, 75, 85, 90, 95, 97, 99],
            15: [1, 25, 40, 50, 55, 65, 70, 75, 85, 85, 90, 96, 99],
            16: [1, 20, 30, 45, 55, 65, 75, 85, 95, 97, 99],
            17: [1, 25, 40, 55, 70, 80, 90, 95, 97, 99]
        },
        'PR': {
            1: [1, 25, 40, 55, 65, 75, 85, 90, 95, 97, 98, 99],
            2: [1, 20, 30, 40, 50, 60, 70, 80, 85, 90, 97, 99],
            3: [1, 25, 35, 45, 50, 60, 70, 80, 85, 90, 95, 99],
            4: [1, 30, 45, 55, 65, 75, 85, 90, 95, 98, 99],
            5: [1, 20, 30, 40, 50, 60, 70, 75, 85, 90, 90, 97, 99],
            6: [1, 25, 35, 45, 50, 60, 70, 75, 85, 90, 90, 96, 99],
            7: [1, 25, 40, 55, 70, 80, 85, 90, 95, 97, 99],
            8: [1, 30, 40, 50, 55, 65, 70, 75, 85, 90, 95, 99],
            9: [1, 20, 30, 45, 55, 65, 75, 85, 90, 95, 97, 99],
            10: [1, 20, 35, 45, 55, 65, 75, 80, 90, 95, 96, 99],
            11: [1, 35, 40, 50, 55, 65, 70, 75, 85, 90, 96, 99],
            12: [1, 50, 70, 80, 85, 90, 95, 96, 98, 99],
            13: [1, 30, 40, 50, 55, 65, 70, 80, 85, 90, 95, 98, 99],
            14: [1, 20, 30, 40, 50, 60, 70, 75, 85, 90, 90, 95, 99],
            15: [1, 30, 40, 50, 60, 70, 75, 80, 90, 90, 96, 99],
            16: [1, 20, 30, 45, 55, 70, 80, 85, 90, 97, 99],
            17: [1, 50, 65, 75, 85, 90, 95, 97, 98, 99]
        }
    }
    if section in score_map[category]:
        if score < len(score_map[category][section]):
            return score_map[category][section][score]
        else:
            return 99
    else:
        return score

class PreguntaHSPQList(APIView):
    def get(self, request):
        Pregunta = pregunta_hspq.objects.all()
        serializer = PreguntaHSPQSerializer(Pregunta, many=True)
        return Response(serializer.data)

class PreguntaHSPQDetails(generics.ListCreateAPIView):
    serializer_class = PreguntaHSPQSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return pregunta_hspq.objects.filter(test_id=pk).order_by('id')

class OpcionHspqView(APIView):
    def get(self, request):
        Opcion = opcion_hspq.objects.all()
        serializer = OpcionHSPQSerializer(Opcion, many=True)
        return Response(serializer.data)

class OpcionHspqDetailAV(generics.ListCreateAPIView):
    serializer_class = OpcionHSPQSerializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return opcion_hspq.objects.filter(pregunta_id=pk)

class Respuesta3AV(generics.CreateAPIView):
    serializer_class = Respuesta3Serializer
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            usuario = self.request.user
            opcion_pk = self.kwargs.get('opcion_pk')
            idOpcion = get_object_or_404(opcion_hspq, pk=opcion_pk)
            serializer.save(usuario_id=usuario, opcion_id=idOpcion)
        else:
            raise PermissionDenied("Usuario no autenticado")

class Respuesta3View(generics.ListAPIView):
    serializer_class = Respuesta3Serializer
    def get_queryset(self):
        pk = self.kwargs['pk']
        return respuesta3.objects.filter(usuario_id=pk)

class UserSectionSumViewHspq(APIView):
    def get(self, request, user_id):
        user_answers = respuesta3.objects.filter(usuario_id=user_id)

        section_sums = user_answers.values('seccion').annotate(total_value=Sum('valor'))

        result = {}
        for item in section_sums:
            section = item['seccion']
            sum = item['total_value']
            if section == 'A':
                sum = convert_section_a(sum)
            elif section == 'C':
                sum = convert_section_c(sum)
            elif section == 'D':
                sum = convert_section_d(sum)
            elif section == 'E':
                sum = convert_section_e(sum)
            elif section == 'F':
                sum = convert_section_f(sum)
            elif section == 'G':
                sum = convert_section_g(sum)
            elif section == 'H':
                sum = convert_section_h(sum)
            elif section == 'I':
                sum = convert_section_i(sum)
            elif section == 'J':
                sum = convert_section_j(sum)
            elif section == 'O':
                sum = convert_section_o(sum)
            elif section == 'Q2':
                sum = convert_section_q2(sum)
            elif section == 'Q3':
                sum = convert_section_q3(sum)
            elif section == 'Q4':
                sum = convert_section_q4(sum)

            result[section] = sum

        custom_order = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']

        ordered_result = {key: result[key] for key in custom_order if key in result}

        return Response(ordered_result)

def convert_section_a(sum):
    if 0 <= sum <= 3:
        return 1
    elif 4 <= sum <= 5:
        return 2
    elif 6 <= sum <= 7:
        return 3
    elif 8 == sum:
        return 4
    elif 9 <= sum <= 10:
        return 5
    elif 11 == sum:
        return 6
    elif 12 <= sum <= 13:
        return 7
    elif 14 <= sum <= 15:
        return 8
    elif 16 == sum:
        return 9
    else:
        return 10
def convert_section_b(sum):
    if 0 <= sum <= 3:
        return 1
    elif 4 == sum:
        return 2
    elif 5 == sum:
        return 3
    elif 6 == sum:
        return 4
    elif 7 == sum:
        return 5
    elif 8 == sum:
        return 6
    elif 9 == sum:
        return 8
    else:
        return 9

def convert_section_c(sum):
    if 0 <= sum <= 5:
        return 1
    elif 6 == sum:
        return 2
    elif 7 <= sum <= 8:
        return 3
    elif 9 <= sum <= 10:
        return 4
    elif 11 == sum:
        return 5
    elif 12 <= sum <= 13:
        return 6
    elif 14 <= sum <= 15:
        return 7
    elif 16 == sum:
        return 8
    elif 17 <= sum <= 18:
        return 9
    else:
        return 10

def convert_section_d(sum):
    if 0 <= sum <= 3:
        return 1
    if 4 <= sum <= 5:
        return 2
    elif 6 <= sum <= 7:
        return 3
    elif 8 == sum:
        return 4
    elif 9 <= sum <= 10:
        return 5
    elif 11 <= sum <= 12:
        return 6
    elif 13 == sum:
        return 7
    elif 14 <= sum <= 15:
        return 8
    elif 16 <= sum <= 17:
        return 9
    else:
        return 10

def convert_section_e(sum):
    if 0 <= sum <= 3:
        return 1
    elif 4 == sum:
        return 2
    elif 5 == sum:
        return 3
    elif 6 <= sum <= 7:
        return 4
    elif 8 == sum:
        return 5
    elif 9 <= sum <= 10:
        return 6
    elif 11 == sum:
        return 7
    elif 12 <= sum <= 13:
        return 8
    elif 14 <= sum <= 15:
        return 9
    else:
        return 10

def convert_section_f(sum):
    if 0 <= sum <= 3:
        return 1
    elif 4 <= sum <= 5:
        return 2
    elif 6 <= sum <= 7:
        return 3
    elif 8 == sum:
        return 4
    elif 9 <= sum <= 10:
        return 5
    elif 11 <= sum <= 12:
        return 6
    elif 13 == sum:
        return 7
    elif 14 <= sum <= 15:
        return 8
    elif 16 == sum:
        return 9
    else:
        return 10

def convert_section_g(sum):
    if 0 <= sum <= 5:
        return 1
    elif 6 <= sum <= 7:
        return 2
    elif 8 <= sum <= 9:
        return 3
    elif 10 == sum:
        return 4
    elif 11 <= sum <= 12:
        return 5
    elif 13 == sum:
        return 6
    elif 14 <= sum <= 15:
        return 7
    elif 16 <= sum <= 17:
        return 8
    elif 18 == sum:
        return 9
    else:
        return 10

def convert_section_h(sum):
    if 0 <= sum <= 2:
        return 1
    elif 3 <= sum <= 4:
        return 2
    elif 5 <= sum <= 6:
        return 3
    elif 7 <= sum <= 8:
        return 4
    elif 9 <= sum <= 10:
        return 5
    elif 11 <= sum <= 12:
        return 6
    elif 13 <= sum <= 14:
        return 7
    elif 15 == sum:
        return 8
    elif 16 <= sum <= 17:
        return 9
    else:
        return 10

def convert_section_i(sum):
    if 0 <= sum <= 1:
        return 1
    elif 2 == sum:
        return 2
    elif 3 == sum:
        return 3
    elif 4 <= sum <= 5:
        return 4
    elif 6 <= sum <= 7:
        return 5
    elif 8 <= sum <= 9:
        return 6
    elif 10 <= sum <= 11:
        return 7
    elif 12 <= sum <= 13:
        return 8
    elif 14 <= sum <= 15:
        return 9
    else:
        return 10

def convert_section_j(sum):
    if 0 <= sum <= 3:
        return 1
    elif 4 == sum:
        return 2
    elif 5 == sum:
        return 3
    elif 6 <= sum <= 7:
        return 4
    elif 8 == sum:
        return 5
    elif 9 <= sum <= 10:
        return 6
    elif 11 == sum:
        return 7
    elif 12 <= sum <= 13:
        return 8
    elif 14 <= sum <= 15:
        return 9
    else:
        return 10

def convert_section_o(sum):
    if 0 <= sum <= 2:
        return 1
    elif 3 == sum:
        return 2
    elif 4 <= sum <= 5:
        return 3
    elif 6 == sum:
        return 4
    elif 7 <= sum <= 8:
        return 5
    elif 9 == sum:
        return 6
    elif 10 <= sum <= 11:
        return 7
    elif 12 <= sum <= 13:
        return 8
    elif 14 <= sum <= 15:
        return 9
    else:
        return 10

def convert_section_q2(sum):
    if 0 <= sum <= 4:
        return 1
    elif 5 == sum:
        return 2
    elif 6 == sum:
        return 3
    elif 7 <= sum <= 8:
        return 4
    elif 9 == sum:
        return 5
    elif 10 <= sum <= 11:
        return 6
    elif 12 <= sum <= 13:
        return 7
    elif 14 == sum:
        return 8
    elif 15 <= sum <= 16:
        return 9
    else:
        return 10

def convert_section_q3(sum):
    if 0 <= sum <= 4:
        return 1
    elif 5 <= sum <= 6:
        return 2
    elif 7 == sum:
        return 3
    elif 8 <= sum <= 9:
        return 4
    elif 10 == sum:
        return 5
    elif 11 <= sum <= 12:
        return 6
    elif 13 <= sum <= 14:
        return 7
    elif 15 == sum:
        return 8
    elif 16 <= sum <= 17:
        return 9
    else:
        return 10

def convert_section_q4(sum):
    if 0 <= sum <= 4:
        return 1
    elif 5 == sum:
        return 2
    elif 6 <= sum <= 7:
        return 3
    elif 8 <= sum <= 9:
        return 4
    elif 10 <= sum <= 11:
        return 5
    elif 12 == sum:
        return 6
    elif 13 <= sum <= 14:
        return 7
    elif 15 <= sum <= 16:
        return 8
    elif 17 == sum:
        return 9
    else:
        return 10
class ResultSegundoOrden(APIView):
    def get(self, request, user_id):
        user_answers = respuesta3.objects.filter(usuario_id=user_id)

        section_sums = user_answers.values('seccion').annotate(total_value=Sum('valor'))

        result = {}
        for item in section_sums:
            section = item['seccion']
            sum = item['total_value']
            if section == 'A':
                sum = convert_section_a(sum)
            elif section == 'C':
                sum = convert_section_c(sum)
            elif section == 'D':
                sum = convert_section_d(sum)
            elif section == 'E':
                sum = convert_section_e(sum)
            elif section == 'F':
                sum = convert_section_f(sum)
            elif section == 'G':
                sum = convert_section_g(sum)
            elif section == 'H':
                sum = convert_section_h(sum)
            elif section == 'I':
                sum = convert_section_i(sum)
            elif section == 'J':
                sum = convert_section_j(sum)
            elif section == 'O':
                sum = convert_section_o(sum)
            elif section == 'Q2':
                sum = convert_section_q2(sum)
            elif section == 'Q3':
                sum = convert_section_q3(sum)
            elif section == 'Q4':
                sum = convert_section_q4(sum)

            result[section] = sum

        print(result)

        custom_order = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']

        ordered_result = {key: result[key] for key in custom_order if key in result}

        return Response(ordered_result)

def convert_and_multiply_section(sum, section):
    if section == 'A':
        result1 = convert_section_a(sum) * 0
        result2 = convert_section_a(sum) * 0
    elif section == 'C':
        result1 = convert_section_c(sum) * 0
        result2 = convert_section_c(sum) * 2
    elif section == 'D':
        result1 = convert_section_d(sum) * 1
        result2 = convert_section_d(sum) * 0
    elif section == 'E':
        result1 = convert_section_e(sum) * 0
        result2 = convert_section_e(sum) * 0
    elif section == 'F':
        result1 = convert_section_f(sum) * 1
        result2 = convert_section_f(sum) * 0
    elif section == 'G':
        result1 = convert_section_g(sum) * 0
        result2 = convert_section_g(sum) * 4
    elif section == 'H':
        result1 = convert_section_h(sum) * 0
        result2 = convert_section_h(sum) * 1
    elif section == 'I':
        result1 = convert_section_i(sum) * 0
        result2 = convert_section_i(sum) * 0
    elif section == 'J':
        result1 = convert_section_j(sum) * 0
        result2 = convert_section_j(sum) * 0
    elif section == 'O':
        result1 = convert_section_o(sum) * 1
        result2 = convert_section_o(sum) * 0
    elif section == 'Q2':
        result1 = convert_section_q2(sum) * 0
        result2 = convert_section_q2(sum) * 0
    elif section == 'Q3':
        result1 = convert_section_q3(sum) * 0
        result2 = convert_section_q3(sum) * 3
    elif section == 'Q4':
        result1 = convert_section_q4(sum) * 0
        result2 = convert_section_q4(sum) * 0
    else:
        result1 = sum
        result2 = sum
    return result1, result2

def sum_first_results(sum, sections):
    total = 0
    for section in sections:
        result1, _ = convert_and_multiply_section(sum, section)
        total += result1
    total += 99
    return total
def sum_second_results(sum, sections):
    total = 0
    for section in sections:
        _, result2 = convert_and_multiply_section(sum, section)
        total += result2
    return total

def subtract_results(sum, section):
    first_results_sum = sum_first_results(sum, section)
    second_results_sum = sum_second_results(sum, section)
    subtraction_result = first_results_sum - second_results_sum
    return subtraction_result * 0.1


# @api_view(['GET', 'POST'])
# def usuario_list(request):
#     if request.method == 'GET':
#         Usuario = usuario.objects.all()
#         serializer = UsuarioSerializer(Usuario, many=True)
#         return Response(serializer.data) 
    
#     if request.method == 'POST':
#         de_serializer = UsuarioSerializer(request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors)

# @api_view(['GET','PUT','DELETE'])
# def usuario_detail(request,pk):
#     if request.method == 'GET':
#         try:
#             Usuario = usuario.objects.get(pk=pk)
#             serializer = UsuarioSerializer(Usuario)
#             return Response(serializer.data)
#         except usuario.DoesNotExist:
#             return Response({'Error': 'Usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
    
#     if request.method == 'PUT':
#         Usuario = usuario.objects.get(pk=pk)
#         de_serializer = UsuarioSerializer(Usuario, data=request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     if request.method == 'DELETE':
#         try:
#             Usuario = usuario.objects.get(pk=pk)
#             Usuario.delete()
#         except  usuario.DoesNotExist:
#             return Response({'Error': 'Usuario no existe'}, status=status.HTTP_404_NOT_FOUND)
#         return Response(status=status.HTTP_204_NO_CONTENT)
       