from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import HttpResponse  
import jwt  


JWT_SECRET = 'piwis123Wquipo'

# Función para generar tokens JWT
def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'user_type': 'admin' if user.is_admin else 'customer' if user.is_customer else 'employee'
        
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# ...

# Create your views here.
def index(request):
    return render(request,'index.html')

def registroAdmin(request):
    if request.method == 'POST':
        # Define el formulario personalizado directamente en la vista
        form = forms.Form(request.POST)
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('admin', 'Administrador')], required=True)

        #validar campos
        if form.is_valid():
            # Procesa el formulario aquí
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_type = form.cleaned_data['user_type']
            # Crea el usuario en la base de datos y establece que es administrador
            user = User.objects.create_user(username=username, email=email, password=password)
            if user_type == 'admin':
                user.is_admin=True
            user.save()

            
            token = generate_jwt_token(user)
            # Envía el token al cliente en la respuesta HTTP
            response = render(request, 'admin.html')  
            response.set_cookie('token', token, httponly=True, secure=True)  # Almacena el token en una cookie (mejora la seguridad)            return response

            return redirect('login')
    else:
        # Define el formulario personalizado directamente en la vista
        form = forms.Form()
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('admin', 'Administrador')], required=True)
    return render(request, 'registro_admin.html', {'form': form})


def registro(request):
    if request.method == 'POST':
        # Define el formulario personalizado directamente en la vista
        form = forms.Form(request.POST)
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('customer', 'Cliente'), ('employee', 'Cuidador')], required=True)

        if form.is_valid():
            # Procesa el formulario aquí
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_type = form.cleaned_data['user_type']
            # Crea el usuario en la base de datos y establece si es cuidador o usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            if user_type == 'customer':
                user.is_customer = True
            elif user_type == 'employee':
                user.is_employee = True
            elif user_type=='admin':
                user.is_admin=True
            user.save()
            return redirect('login')
    else:
        # Define el formulario personalizado directamente en la vista
        form = forms.Form()
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('customer', 'Cliente'), ('employee', 'Cuidador')], required=True)
    return render(request, 'registro.html', {'form': form})




def login_view(request):
    if request.method == 'POST':
        form = forms.Form(request.POST)
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['password'] = forms.CharField(widget=forms.PasswordInput, required=True)
        
        if form.is_valid():
            # Procesa el formulario aquí
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                token = generate_jwt_token(user)

                # Envía el token al cliente en la respuesta HTTP
                
                if user.is_admin:
                    response = render(request, 'admin.html')  # Puedes ajustar la respuesta según tus necesidades
                    response.set_cookie('token', token, httponly=True, secure=True)  # Almacena el token en una cookie (mejora la seguridad)
                    return response
                elif user.is_customer:
                    response = render(request, 'customer.html')  # Puedes ajustar la respuesta según tus necesidades
                    response.set_cookie('token', token, httponly=True, secure=True)  # Almacena el token en una cookie (mejora la seguridad)
                    return response
                elif user.is_employee:
                    response = render(request, 'employee.html')  # Puedes ajustar la respuesta según tus necesidades
                    response.set_cookie('token', token, httponly=True, secure=True)  # Almacena el token en una cookie (mejora la seguridad)
                    return response
            
        # Si el formulario no es válido o el usuario no existe, muestra el formulario de inicio de sesión con un mensaje de error
        return render(request, 'login.html', {'error': 'nombre de usuario o contraseña inválidos'})
    
    # Si el método no es POST, muestra el formulario de inicio de sesión
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    # Elimina el token almacenado en la cookie al cerrar la sesión
    response = render(request, 'login.html')
    response.delete_cookie('token')
    return render(request,'login.html')

def employee(request):
    return render(request, "employee.html")