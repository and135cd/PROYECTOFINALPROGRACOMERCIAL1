from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Importa las configuraciones de Django
import jwt
from datetime import timedelta, datetime

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
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    telefono = models.CharField(max_length=15)

class Cuidador(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    telefono = models.CharField(max_length=15)

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=100, choices=[('Perro', 'Perro'),
        ('Gato', 'Gato'),
        ('Pez', 'Pez'),
        ('Pájaro', 'Pájaro'),
        ('Conejo', 'Conejo'),
        ('Hamster', 'Hamster'),
        ('Cobaya', 'Cobaya'),
        ('Reptil', 'Reptil'),
        ('Conejillo de Indias', 'Conejillo de Indias'),
        ('Hurón', 'Hurón'),
        ('Otro', 'Otro'),])
    genero = models.CharField(max_length=10, choices=[('Macho', 'Macho'), ('Hembra', 'Hembra')]) 
    raza = models.CharField(max_length=100)
    edad = models.IntegerField()
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre 

class TipoDeCuidado(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre 

class SolicitudDeCuidado(models.Model):
    fecha_solicitud = models.DateField()
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    fecha_fin = models.DateField(blank=True, null=True) 
    hora_fin = models.TimeField()
    ubicacion_servicio = models.CharField(max_length=200, null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20)
    tipo_de_cuidado = models.ForeignKey(TipoDeCuidado, on_delete=models.CASCADE)
    cuidadores_aceptan = models.ManyToManyField(Cuidador, related_name='solicitudes_aceptadas')
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    mascotas = models.ManyToManyField(Mascota, related_name='solicitudes_de_alojamiento')
    precio=models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    # Aquí agregas tu método para calcular precio
    def calcular_precio(self):
        # Define tus tarifas aquí
        tarifas = {
            'Alojamiento': 20.0,  # precio por día
            'Paseo': 10.0,        # precio por hora
            'Guarderia': 15.0,    # precio por día
            'Peluqueria': 30.0,   # precio fijo por servicio
        }

        # Calcula la duración según si tienes fechas o horas
        duracion = 0
        if self.fecha_inicio and self.fecha_fin:
            duracion = (self.fecha_fin - self.fecha_inicio).days + 1
        elif self.hora_inicio and self.hora_fin:
            # Aquí conviertes las horas en objetos datetime para poder calcular la duración
            inicio = datetime.combine(datetime.today(), self.hora_inicio)
            fin = datetime.combine(datetime.today(), self.hora_fin)
            duracion = (fin - inicio).total_seconds() / 3600  # Convertir segundos a horas

        # Aplica la tarifa correspondiente
        tipo_cuidado = self.tipo_de_cuidado.nombre
        if tipo_cuidado in tarifas:
            precio_base = tarifas[tipo_cuidado]
            if tipo_cuidado == 'Paseo' or tipo_cuidado == 'Peluqueria':
                self.precio = precio_base * duracion
            else:  # Alojamiento y Guarderia se cobran por día
                self.precio = precio_base * max(duracion, 1)  # Asegura al menos un día

    def save(self, *args, **kwargs):
        # Asegúrate de llamar a calcular_precio antes de guardar la instancia
        self.calcular_precio()
        super(SolicitudDeCuidado, self).save(*args, **kwargs)
    
    def aceptar(self, cuidador):
        self.estado = 'Aceptada'
        self.cuidadores_aceptan.add(cuidador)
        self.save()

    def rechazar(self, cuidador):
        self.estado = 'Rechazada'
        self.cuidadores_aceptan.remove(cuidador)
        self.save()

class Conversacion(models.Model):
    solicitud_de_cuidado = models.ForeignKey(SolicitudDeCuidado, on_delete=models.CASCADE)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_y_hora = models.DateTimeField(auto_now_add=True)

class MascotaSolicitud(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    solicitud_de_cuidado = models.ForeignKey(SolicitudDeCuidado, on_delete=models.CASCADE)
