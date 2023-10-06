from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Importa las configuraciones de Django
import jwt
# Create your models here.


class User(AbstractUser):
    is_admin=models.BooleanField('is_admin', default=False)#administrador
    is_customer=models.BooleanField('is_customer', default=False)#propietario de mascotas
    is_employee=models.BooleanField('is_employee', default=False)# cuidador de mascotas

    def get_token(self):
            payload = {
                'username': self.username,
                'password': self.password,
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return token
    

class Propietario(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)

class Cuidador(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=[('Macho', 'Macho'), ('Hembra', 'Hembra')]) 
    raza = models.CharField(max_length=100)
    edad = models.IntegerField()
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)

class TipoDeCuidado(models.Model):
    nombre = models.CharField(max_length=100)

class SolicitudDeCuidado(models.Model):
    fecha_solicitud = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    descripcion = models.TextField()
    estado = models.CharField(max_length=20)
    tipo_de_cuidado = models.ForeignKey(TipoDeCuidado, on_delete=models.CASCADE)
    cuidadores_aceptan = models.ManyToManyField(Cuidador, related_name='solicitudes_aceptadas')
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)

class Conversacion(models.Model):
    solicitud_de_cuidado = models.ForeignKey(SolicitudDeCuidado, on_delete=models.CASCADE)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_y_hora = models.DateTimeField(auto_now_add=True)

