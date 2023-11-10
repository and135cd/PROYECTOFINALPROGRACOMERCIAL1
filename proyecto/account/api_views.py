from django.contrib.auth.models import User
from account.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect
from . import forms

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
    
    
