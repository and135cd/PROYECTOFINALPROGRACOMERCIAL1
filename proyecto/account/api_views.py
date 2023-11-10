from django.contrib.auth.models import User
from account.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login
import jwt
from django.conf import settings

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
