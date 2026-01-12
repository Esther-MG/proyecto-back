from rest_framework import serializers
#from django.contrib.auth.models import User
from usuarios.models import User

class RegistrarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password':{ 'write_only':True}
        }
        
    def save(self):
        if User.objects.filter(username=self.validated_data['username']).exists():
            raise serializers.ValidationError({'El ci ya existe'})
    
        account = User(
            username = self.validated_data['username'],
            first_name = self.validated_data['first_name'],
            last_name = self.validated_data['last_name'],
            email = self.validated_data['email'],
            edad = self.validated_data['edad'],
            colegio = self.validated_data['colegio'],
            sexo = self.validated_data['sexo'],
            celular = self.validated_data['celular'],
            grado_escolar = self.validated_data['grado_escolar'],

        )
        account.set_password(self.validated_data['password'])
        account.save()
        return account
    
class RegistrarAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password':{ 'write_only':True}
        }
        
    def save(self):
        if User.objects.filter(username=self.validated_data['username']).exists():
            raise serializers.ValidationError({'El ci ya existe'})
    
        account = User(
            username = self.validated_data['username'],
            first_name = self.validated_data['first_name'],
            last_name = self.validated_data['last_name'],
            email = self.validated_data['email'],
            edad = self.validated_data['edad'],
            sexo = self.validated_data['sexo'],
        )
        account.set_password(self.validated_data['password'])
        account.save()
        return account

class UpdateTestFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8', 'test9']

    def update(self, instance, validated_data):
        instance.test1 = validated_data.get('test1', instance.test1)
        instance.test2 = validated_data.get('test2', instance.test2)
        instance.test3 = validated_data.get('test3', instance.test3)
        instance.test4 = validated_data.get('test4', instance.test4)
        instance.test5 = validated_data.get('test5', instance.test5)
        instance.test6 = validated_data.get('test6', instance.test6)
        instance.test7 = validated_data.get('test7', instance.test7)
        instance.test8 = validated_data.get('test8', instance.test8)
        instance.test9 = validated_data.get('test9', instance.test9)
        instance.save()
        return instance