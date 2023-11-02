from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import HttpResponse  
import jwt  
from django.contrib.auth.decorators import login_required
from .forms import PropietarioForm, MascotaForm, AlojamientoForm
from .models import Propietario, Mascota, SolicitudDeCuidado, TipoDeCuidado
from datetime import datetime, timedelta
from datetime import date 
from django.contrib import messages 
from django.core.exceptions import ObjectDoesNotExist


JWT_SECRET = 'piwis123Wquipo'

# Función para generar tokens JWT
def generate_jwt_token(user):
    expiration_time = datetime.now() + timedelta(minutes=30)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'user_type': 'admin' if user.is_admin else 'customer' if user.is_customer else 'employee',
        'exp': expiration_time.timestamp()  
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

# ...

# Create your views here.
def index(request):
    return render(request,'index2.html')
    

@login_required
def tipos_cuidados(request):
    return render(request,'cuidados/tipos_cuidados.html')

@login_required
def cuidados(request):
    return render(request,'cuidados/tipos_cuidados copy.html')

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

def inicio(request):
    return render(request, 'inicio.html')


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
                context={
                    'user':request.user,
                }
                # Envía el token al cliente en la respuesta HTTP
                
                if user.is_admin:
                    response = render(request, 'admin.html',context) 
                    response.set_cookie('token', token, httponly=True, secure=True)  
                    return response
                elif user.is_customer:
                    response = redirect('customer') 
                    response.set_cookie('token', token, httponly=True, secure=True)  
                    return response
                elif user.is_employee:
                    response = render(request, 'employee.html',context) 
                    response.set_cookie('token', token, httponly=True, secure=True) 
                    return response
            
        # Si el formulario no es válido o el usuario no existe, muestra el formulario de inicio de sesión con un mensaje de error
        return render(request, 'login.html', {'error': 'nombre de usuario o contraseña inválidos'})
    
    # Si el método no es POST, muestra el formulario de inicio de sesión
    return render(request, 'login.html')

def logout_view(request):
    # Crea la respuesta primero
    response = redirect('login')
    # Elimina el token almacenado en la cookie al cerrar la sesión
    response.delete_cookie('token')
    # Luego, realiza el cierre de sesión
    logout(request)
    return response


def employee(request):
    context={
        'user':request.user,
    }
    return render(request, "employee.html",context)

@login_required
def registrar_datos_propietario(request):
    # Obtén el token actual del usuario autenticado
    current_token = request.COOKIES.get('token')
    from_menu = request.GET.get('from_menu')  # Verifica si el usuario viene de hacer clic en "Mascotas"

    try:
        # Intenta obtener los datos de propietario del usuario actual
        propietario = Propietario.objects.get(user=request.user)
        
        # Si ya existen datos de propietario, carga esos datos en el formulario para su edición
        if request.method == 'POST':
            form = PropietarioForm(request.POST, instance=propietario)
        else:
            form = PropietarioForm(instance=propietario)
    except Propietario.DoesNotExist:
        # Si no existen datos de propietario, crea un nuevo formulario para la creación
        if request.method == 'POST':
            form = PropietarioForm(request.POST)
        else:
            form = PropietarioForm()
    
    if request.method == 'POST':
        if form.is_valid():
            propietario = form.save(commit=False)
            propietario.user = request.user
            propietario.save()
            
            # Verifica si el usuario viene de hacer clic en "Mascotas" y redirige en consecuencia
            if from_menu:
                return redirect('listar_mascotas')
            else:
                return redirect('customer')

    # Renderiza la página de registro y establece el token en la cookie
    response = render(request, 'registro_datos_propietario.html', {'form': form})
    response.set_cookie('token', current_token, httponly=True, secure=True)
    
    return response



@login_required
def listar_datos_propietario(request):
    try:
        # Intenta obtener los datos de propietario del usuario actual
        propietario = Propietario.objects.get(user=request.user)

        context = {
            'propietario': propietario,
        }
        return render(request, 'listar_datos_propietario.html', context)
    except Propietario.DoesNotExist:
        # Maneja el caso en el que no existen datos de propietario
        return render(request, 'registro_datos_propietario.html')
    

@login_required
def editar_datos_propietario(request):
    try:
        propietario = Propietario.objects.get(user=request.user)

        if request.method == 'POST':
            form = PropietarioForm(request.POST, instance=propietario)
            if form.is_valid():
                form.save()
                return redirect('listar_datos_propietario')
        else:
            form = PropietarioForm(instance=propietario)

        context = {
            'form': form,
        }
        return render(request, 'editar_datos_propietario.html', context)
    except Propietario.DoesNotExist:
        return render(request, 'sin_datos_propietario.html')
    

def customer(request):
    # Obtén el token actual del usuario autenticado
    current_token = request.COOKIES.get('token')
    # Verifica si el usuario autenticado ya tiene un propietario asociado
    try:
        propietario = Propietario.objects.get(user_id=request.user.id)
        propietario_nombre = f"{propietario.nombre} {propietario.apellido}"
    except Propietario.DoesNotExist:
        propietario_nombre = None

    context = {
        'user': request.user,
        'propietario_nombre': propietario_nombre,
    }
    # Renderiza la página de customer y establece el token en la cookie
    response = render(request, 'customer.html', context)
    response.set_cookie('token', current_token, httponly=True, secure=True)
    
    return redirect('inicio')

@login_required
def listar_mascotas(request):
    if request.user.is_customer:  # Verifica si el usuario autenticado es un propietario
        if hasattr(request.user, 'propietario'):
            propietario = request.user.propietario

            # Filtra las mascotas asociadas al propietario actual
            mascotas = Mascota.objects.filter(propietario=propietario)

            return render(request, 'mascotas/listar_mascotas.html', {'mascotas': mascotas})
        else:
            # Si el usuario no tiene un propietario, muestra un mensaje y redirige a la página para registrar datos de propietario
            messages.warning(request, 'Debes ingresar tus datos de propietario primero.')
            print("si se envia el mensaje")
            return redirect('registro_datos_propietario')
    else:
        # Maneja el caso en el que el usuario no sea un propietario
        return HttpResponse('No tienes permiso para acceder a esta página.')
    
@login_required
def agregar_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            propietario = Propietario.objects.get(user=request.user)
            mascota = form.save(commit=False)
            mascota.propietario = propietario
            mascota.save()
            return redirect('listar_mascotas')
    else:
        form = MascotaForm()
    return render(request, 'mascotas/agregar_mascota.html', {'form': form})

@login_required
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    
    # Verifica si la mascota pertenece al propietario autenticado
    if mascota.propietario != request.user.propietario:
        return HttpResponse('No tienes permiso para editar esta mascota.')

    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('listar_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'mascotas/editar_mascota.html', {'form': form})

@login_required
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    
    # Verifica si la mascota pertenece al propietario autenticado
    if mascota.propietario != request.user.propietario:
        return HttpResponse('No tienes permiso para eliminar esta mascota.')

    if request.method == 'POST':
        mascota.delete()
        return redirect('listar_mascotas')
    return render(request, 'mascotas/eliminar_mascota.html', {'mascota': mascota})


#cuidados
@login_required
def publicar_alojamiento(request):
    if request.method == 'POST':
        form = AlojamientoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.propietario = request.user.propietario
            solicitud.estado = 'Pendiente'
            
            # Intenta obtener el objeto TipoDeCuidado con el nombre 'Alojamiento'
            try:
                tipo_alojamiento = TipoDeCuidado.objects.get(nombre='Alojamiento')
            except ObjectDoesNotExist:
                messages.error(request, "No se pudo encontrar el tipo de cuidado 'Alojamiento'.")
                return render(request, 'cuidados/publicar_alojamiento.html', {'form': form})
            
            solicitud.tipo_de_cuidado = tipo_alojamiento
            
            # Obtiene las coordenadas de la ubicación desde el formulario
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                try:
                    lat, lng = map(float, ubicacion.split(','))
                    solicitud.latitud = lat
                    solicitud.longitud = lng
                except ValueError:
                    messages.error(request, "La ubicación proporcionada es inválida.")
                    return render(request, 'cuidados/publicar_alojamiento.html', {'form': form})
                
            solicitud.save()
            form.save_m2m()  # Guarda las relaciones ManyToMany con las mascotas
            
            messages.success(request, "La solicitud de alojamiento ha sido publicada con éxito.")
            return redirect('listar_solicitudes_de_cuidado')
    else:
        form = AlojamientoForm()
        # Filtra las mascotas del propietario autenticado
        propietario = request.user.propietario
        form.fields['mascotas'].queryset = Mascota.objects.filter(propietario=propietario)

    return render(request, 'cuidados/publicar_alojamiento.html', {'form': form})
@login_required
def listar_solicitudes_de_cuidado(request):
    propietario = request.user.propietario
    solicitudes = SolicitudDeCuidado.objects.filter(propietario=propietario)
    return render(request, 'cuidados/listar_solicitudes.html', {'solicitudes': solicitudes})