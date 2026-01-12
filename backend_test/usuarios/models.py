from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    edad = models.IntegerField(blank=True, null=True)
    colegio = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.CharField(max_length=100,blank=True, null=True)
    celular = models.CharField(max_length=50, blank=True, null=True)
    grado_escolar = models.CharField(max_length=50, blank=True, null=True)
    test1 = models.BooleanField(default=True)
    test2 = models.BooleanField(default=False)
    test3 = models.BooleanField(default=False)
    test4 = models.BooleanField(default=False)
    test5 = models.BooleanField(default=False)
    test6 = models.BooleanField(default=False)
    test7 = models.BooleanField(default=False)
    test8 = models.BooleanField(default=False)
    test9 = models.BooleanField(default=False)
    
 
    
    
    