from django.db import models
from usuarios.models import User

class tipo_usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre

class usuario(models.Model):
    idUsuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    ci = models.CharField(max_length=200)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=200)
    correo = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    status = models.BooleanField(default=True)
    Tipo_id = models.ForeignKey(tipo_usuario, on_delete=models.CASCADE)
    
    def __str__(self) :
        return self.nombre
#---------------------------------------------------------------------------

class encuesta(models.Model):
    id = models.AutoField(primary_key=True)
    pregunta1= models.TextField(blank=True)
    pregunta2= models.TextField(blank=True)
    pregunta3= models.TextField(blank=True)
    pregunta4= models.TextField(blank=True)
    pregunta5= models.TextField(blank=True)
    pregunta6= models.TextField(blank=True)
    pregunta7= models.TextField(blank=True)
    usuario_id= models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        db_table = "encuesta"
    
    def __str__(self):
        return self.pregunta1

class tutor(models.Model):
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    ci = models.CharField(max_length=200)
    correo = models.CharField(max_length=200)
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class test (models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    instruccion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
class seccion (models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    instruccion = models.TextField(blank=True)
    test_id = models.ForeignKey(test, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre
    
class pregunta_sa(models.Model):
    id = models.AutoField(primary_key=True)
    nro_pregunta = models.IntegerField()
    texto_pregunta = models.CharField(max_length=200)
    imagen = models.CharField(blank=True, max_length=900)
    seccion_id = models.ForeignKey(seccion, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.texto_pregunta
    
class opcion_sa(models.Model):
    id = models.AutoField(primary_key=True)
    inciso = models.CharField(max_length=50)
    respuesta = models.CharField(max_length=200)
    valor = models.BooleanField(default=False)
    pregunta_id = models.ForeignKey(pregunta_sa, on_delete=models.CASCADE)

    def __str__(self):
        return self.respuesta
    
class respuesta1(models.Model):
    id = models.AutoField(primary_key=True)
    id_test = models.IntegerField()
    id_apartado = models.IntegerField()
    id_pregunta = models.IntegerField()
    valor = models.IntegerField()
    opcion_id = models.ForeignKey(opcion_sa, on_delete=models.CASCADE)
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class pregunta_ipp(models.Model):
    id = models.AutoField(primary_key=True)
    nro_pregunta = models.IntegerField()
    texto_pregunta = models.CharField(max_length=500)
    seccion = models.IntegerField()
    categoria = models.CharField(max_length=200)
    test_id = models.ForeignKey(test, on_delete=models.CASCADE)
    def __str__(self):
        return self.texto_pregunta

class opcion_ipp(models.Model):
    id = models.AutoField(primary_key=True)
    inciso = models.CharField(max_length=50)
    respuesta = models.CharField(max_length=200)
    valor = models.IntegerField()
    def __str__(self):
        return self.respuesta

class respuesta2(models.Model):
    id = models.AutoField(primary_key=True)
    id_test = models.IntegerField()
    valor = models.IntegerField()
    categoria = models.CharField(max_length=200)
    seccion = models.IntegerField()
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE)
    pregunta_id = models.ForeignKey(pregunta_ipp, on_delete=models.CASCADE)
    opcion_id = models.ForeignKey(opcion_ipp, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.usuario_id)

class pregunta_hspq(models.Model):
    id = models.AutoField(primary_key=True)
    nro_pregunta = models.IntegerField()
    texto_pregunta = models.CharField(max_length=500)
    seccion = models.CharField(max_length=200)
    test_id = models.ForeignKey(test, on_delete=models.CASCADE)
    def __str__(self):
        return self.texto_pregunta

class opcion_hspq(models.Model):
    id = models.AutoField(primary_key=True)
    inciso = models.CharField(max_length=50)
    respuesta = models.CharField(max_length=200)
    valor = models.IntegerField()
    pregunta_id = models.ForeignKey(pregunta_hspq, on_delete=models.CASCADE)
    def __str__(self):
        return self.respuesta

class respuesta3(models.Model):
    id = models.AutoField(primary_key=True)
    id_test = models.IntegerField()
    id_pregunta = models.IntegerField()
    valor = models.IntegerField()
    seccion = models.CharField(max_length=200)
    usuario_id = models.ForeignKey(User, on_delete=models.CASCADE)
    opcion_id = models.ForeignKey(opcion_hspq, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.usuario_id)