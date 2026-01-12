from rest_framework import serializers
from usuarios_app.models import (usuario, tipo_usuario,tutor, test, seccion, pregunta_sa,
opcion_sa, encuesta, respuesta1, pregunta_ipp, opcion_ipp, respuesta2, pregunta_hspq, opcion_hspq, respuesta3)
from usuarios.models import User
from django.contrib.auth.models import Group

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = tipo_usuario
        fields = "__all__"
        
class UsuarioSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.CharField(source='Tipo_id.nombre')
    class Meta:
        model = usuario
        fields = "__all__"
        #exclude = ['idUsuario']
#------------------------------------------------------------------------
class EncuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = encuesta
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        
class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

class UserGroupSerializer(serializers.Serializer):
    user = UserSerializer()
    group = GroupsSerializer()
    
class TutorSerializer(serializers.ModelSerializer):
    class Meta: 
        model = tutor
        fields = "__all__"

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = test
        fields = "__all__"

class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = seccion
        fields = "__all__"
        
class PreguntaSASerializer(serializers.ModelSerializer):
    class Meta:
        model = pregunta_sa
        fields = "__all__"
        
class OpcionSASerializer(serializers.ModelSerializer):
    class Meta:
        model = opcion_sa
        fields = "__all__"
    
class Respuesta1Serializer(serializers.ModelSerializer):
    class Meta:
        model = respuesta1
        fields = "__all__"

class PreguntaIPPSerializer(serializers.ModelSerializer):
    class Meta:
        model = pregunta_ipp
        fields = "__all__"

class OpcionIPPSerializer(serializers.ModelSerializer):
    class Meta:
        model = opcion_ipp
        fields = "__all__"

class Respuesta2Serializer(serializers.ModelSerializer):
    class Meta:
        model = respuesta2
        fields = "__all__"

class PreguntaHSPQSerializer(serializers.ModelSerializer):
    class Meta:
        model = pregunta_hspq
        fields = "__all__"

class OpcionHSPQSerializer(serializers.ModelSerializer):
    class Meta:
        model = opcion_hspq
        fields = "__all__"

class Respuesta3Serializer(serializers.ModelSerializer):
    class Meta:
        model = respuesta3
        fields = "__all__"

# class UsuarioSerializer(serializers.Serializer):
#     idUsuario = serializers.IntegerField(read_only=True)
#     nombre = serializers.CharField()
#     apellido = serializers.CharField()
#     ci = serializers.CharField()
#     edad = serializers.IntegerField()
#     sexo = serializers.CharField()
#     correo = serializers.CharField()
#     password = serializers.CharField()
#     status = serializers.BooleanField()
#     Tipo_id = serializers.PrimaryKeyRelatedField(queryset=tipo_usuario.objects.all())
    
#     def create(self, validated_data):
#         return usuario.objects.create(**validated_data)
    
#     def update(self, instance, validated_data):
#         instance.nombre = validated_data.get('nombre', instance.nombre)
#         instance.apellido = validated_data.get('apellido', instance.apellido)
#         instance.ci = validated_data.get('ci', instance.ci)
#         instance.edad = validated_data.get('edad', instance.edad)
#         instance.sexo = validated_data.get('sexo', instance.sexo)
#         instance.correo = validated_data.get('correo', instance.correo)
#         instance.password = validated_data.get('password', instance.password)
#         instance.status = validated_data.get('status', instance.status)
#         instance.Tipo_id = validated_data.get('Tipo_id', instance.Tipo_id)
#         instance.save()
#         return instance

# class TipoUsuarioSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     nombre = serializers.CharField()