from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from usuarios.api.serializers import RegistrarSerializer, RegistrarAdminSerializer, UpdateTestFieldsSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group,User
#from usuarios import models
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import auth
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def session_view(request):
    if request.method == "GET":
        user = request.user
        account = User.objects.get(username=user)
        data = {}
        if account is not None:
            data['response'] = 'El usuario esta en sesion'
            data['id'] = account.id
            data['username'] = account.username
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['edad'] = account.edad
            data['sexo'] = account.sexo
            data['colegio'] = account.colegio
            data['celular'] = account.celular
            data['grado_escolar'] = account.grado_escolar
            data['email'] = account.email
            data['test1'] = account.test1
            data['test2'] = account.test2
            data['test3'] = account.test3
            data['test4'] = account.test4
            data['test5'] = account.test5
            data['test6'] = account.test6
            data['test7'] = account.test7
            data['test8'] = account.test8
            data['test9'] = account.test9
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(data)
        else:
            data['error'] = 'El usuario no esta en sesion'
            return Response(data, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST',])
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
        
@api_view(['POST',])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrarSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'Registro de usuario exitoso'
            data['id']= account.id
            data['username'] = account.username
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['edad'] = account.edad
            data['sexo'] = account.sexo
            data['colegio'] = account.colegio
            data['celular'] = account.celular
            data['grado_escolar'] = account.grado_escolar
            data['email'] = account.email
            data['test1'] = account.test1
            data['test2'] = account.test2
            data['test3'] = account.test3
            data['test4'] = account.test4
            data['test5'] = account.test5
            data['test6'] = account.test6
            data['test7'] = account.test7
            data['test8'] = account.test8
            data['test9'] = account.test9
            
            admin_group = Group.objects.get(name='Estudiante')  
            admin_group.user_set.add(account)
            
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        else:
            data = serializer.errors
            
        return Response(data)
    
@api_view(['POST',])
def registration_admin_view(request):
    if request.method == 'POST':
        serializer = RegistrarAdminSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'Registro de usuario exitoso'
            data['id']= account.id
            data['username'] = account.username
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['edad'] = account.edad
            data['sexo'] = account.sexo
            data['email'] = account.email
            
            admin_group = Group.objects.get(name='Administrador') 
            admin_group.user_set.add(account)
            
            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            
        else:
            data = serializer.errors
            
        return Response(data)
            
            
@api_view(['POST',])
def login_view(request):
    data = {}
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')  
        account = auth.authenticate(username=username, password=password)
        if account is not None:
            data['response'] = 'Login successful'
            data['id'] = account.id
            data['username'] = account.username
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name
            data['edad'] = account.edad
            data['sexo'] = account.sexo
            data['colegio'] = account.colegio
            data['celular'] = account.celular
            data['grado_escolar'] = account.grado_escolar
            data['email'] = account.email

            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(data)

        else:
            data['error'] = 'Credenciales incorrectas'
            return Response(data, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def update_test_fields_view(request, usuario_id):
    try:
        user = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateTestFieldsSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
