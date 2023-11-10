from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Propietario, Cuidador, Mascota, TipoDeCuidado, SolicitudDeCuidado, Conversacion, MascotaSolicitud

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin', 'is_customer', 'is_employee']

class PropietarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propietario
        fields = ['id', 'user', 'nombre', 'apellido', 'direccion', 'latitud', 'longitud', 'telefono']

class CuidadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuidador
        fields = ['id', 'user', 'nombre', 'apellido', 'direccion', 'latitud', 'longitud', 'telefono']

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'especie', 'genero', 'raza', 'edad', 'propietario']

class TipoDeCuidadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDeCuidado
        fields = ['id', 'nombre']

class SolicitudDeCuidadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDeCuidado
        fields = [
            'id', 'fecha_solicitud', 'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin',
            'ubicacion_servicio', 'latitud', 'longitud', 'descripcion', 'estado',
            'tipo_de_cuidado', 'cuidadores_aceptan', 'propietario', 'mascotas', 'precio'
        ]

class ConversacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversacion
        fields = ['id', 'solicitud_de_cuidado', 'cuidador', 'propietario', 'mensaje', 'fecha_y_hora']

class MascotaSolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = MascotaSolicitud
        fields = ['id', 'mascota', 'solicitud_de_cuidado']
