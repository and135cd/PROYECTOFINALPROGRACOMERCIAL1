from django.contrib.auth.models import User
from account.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from . import forms
from django.contrib.auth import authenticate, login
import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from rest_framework.response import Response
from django.utils import timezone
from .models import SolicitudDeCuidado
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from geopy.distance import geodesic
from .models import Propietario, Cuidador, User
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

@csrf_exempt
@require_POST
def registro_api(request):
    data = request.POST
    form = forms.UserForm(data)

    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']
        user_type = form.cleaned_data['user_type']

        if password != password2:
            return JsonResponse({'error': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Ya existe ese usuario.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        if user_type == 'customer':
            user.is_customer = True
        elif user_type == 'employee':
            user.is_employee = True
        user.save()

        return JsonResponse({'success': 'El usuario ha sido registrado exitosamente.'})
    else:
        return JsonResponse({'error': 'Datos de formulario no válidos.'})
    

@csrf_exempt
@require_POST
def login_api(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Genera el token JWT
        token = jwt.encode({'username': user.username, 'id': user.id}, settings.SECRET_KEY, algorithm='HS256')
        
        # Información de usuario y token para la respuesta
        user_data = {
            'username': user.username,
            'is_admin': user.is_admin,
            'is_customer': user.is_customer,
            'is_employee': user.is_employee,
            'token': token
        }
        return JsonResponse({'success': 'Inicio de sesión exitoso', 'user': user_data})

    return JsonResponse({'error': 'Nombre de usuario o contraseña inválidos'}, status=401)

@csrf_exempt
@require_http_methods(["GET"])
def employee_inicio(request):
    # Obtener la fecha actual
    hoy = timezone.now().date()
    cuidador = request.user.cuidador

    # Encuentra las solicitudes de cuidado para el día actual
    solicitudes_hoy = SolicitudDeCuidado.objects.filter(
        fecha_inicio=hoy, 
        cuidadores_aceptan=cuidador
    ).order_by('hora_inicio')
    
    # Si hay solicitudes para hoy, toma la primera para el recordatorio
    proxima_cita = solicitudes_hoy.first()

    # Preparar los datos para la respuesta
    if proxima_cita:
        proxima_cita_data = {
            "fecha_inicio": proxima_cita.fecha_inicio.strftime('%Y-%m-%d'),
            "hora_inicio": proxima_cita.hora_inicio.strftime('%H:%M'),
            # Puedes agregar más campos según sea necesario
        }
    else:
        proxima_cita_data = None

    return JsonResponse({'proxima_cita': proxima_cita_data})

@csrf_exempt
@require_POST
def logout_api(request):
    # Crea la respuesta primero
    response = JsonResponse({'success': 'Cierre de sesión exitoso'})

    # Elimina el token almacenado en la cookie al cerrar la sesión
    response.delete_cookie('token')

    # Luego, realiza el cierre de sesión
    logout(request)

    return response


@require_http_methods(["GET"])
def inicio_api(request,username):
    
    try:
        # Encuentra al usuario por username y luego al propietario asociado
        user = User.objects.get(username=username)
        propietario = Propietario.objects.get(user=user)
        propietario_location = (propietario.latitud, propietario.longitud)

        todos_los_cuidadores = Cuidador.objects.all()
        cuidadores_cercanos = []

        for cuidador in todos_los_cuidadores:
            cuidador_location = (cuidador.latitud, cuidador.longitud)
            distance = geodesic(propietario_location, cuidador_location).km
            if distance <= 2:
                cuidador.distance = distance
                cuidadores_cercanos.append({
                    'nombre': cuidador.nombre,
                    'apellido':cuidador.apellido,
                    'latitud': cuidador.latitud,
                    'longitud': cuidador.longitud,
                    'distance': distance,
                })

        cuidadores_cercanos.sort(key=lambda x: x['distance'])

        # Preparar datos para la respuesta JSON
        response_data = {'cuidadores_cercanos': cuidadores_cercanos}
        return JsonResponse(response_data)

    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Propietario.DoesNotExist:
        return JsonResponse({'error': 'No se encontró el propietario'}, status=404)