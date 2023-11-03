from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.http import HttpResponse  
import jwt  
from django.contrib.auth.decorators import login_required
from .forms import PropietarioForm, MascotaForm, AlojamientoForm, CuidadorForm, PaseoForm
from .models import Propietario, Mascota, SolicitudDeCuidado, TipoDeCuidado, Cuidador
from datetime import datetime, timedelta
from datetime import date 
from django.contrib import messages 
from django.core.exceptions import ObjectDoesNotExist
from geopy.distance import geodesic


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
    if request.user.is_customer:
        try:
            propietario = request.user.propietario
        except Propietario.DoesNotExist:
            messages.warning(request, 'Debes registrar tus datos de propietario primero.')
            return redirect('registro_datos_propietario')

        # Verifica si el propietario tiene al menos una mascota registrada
        mascotas = Mascota.objects.filter(propietario=propietario)
        if not mascotas:
            messages.warning(request, 'Debes registrar al menos una mascota para publicar un anuncio.')
            return redirect('agregar_mascota')  

        # Si tiene un perfil de propietario y al menos una mascota, muestra la página de cuidados
        return render(request, 'cuidados/tipos_cuidados copy.html')
    else:
        messages.error(request, 'No tienes permiso para ver esta página.')
        return redirect('inicio')
    

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
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            user_type = form.cleaned_data['user_type']

            # Comprueba si las contraseñas coinciden
            if password != password2:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, 'registro.html', {'form': form})

            # Comprueba si el nombre de usuario ya existe
            if User.objects.filter(username=username).exists():
                messages.warning(request, "Ya existe ese usuario.")
                return render(request, 'registro.html', {'form': form})

            # Si el nombre de usuario no existe, crea el nuevo usuario
            user = User.objects.create_user(username=username, email=email, password=password)
            if user_type == 'customer':
                user.is_customer = True
            elif user_type == 'employee':
                user.is_employee = True
            user.save()

            messages.success(request, "El usuario ha sido registrado exitosamente.")
            return redirect('login')
    else:
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

#empleado
def employee(request):
    context={
        'user':request.user,
    }
    return render(request, "employee.html",context)


@login_required
def registrar_datos_cuidador(request):
    current_token = request.COOKIES.get('token')
    cuidador, created = Cuidador.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CuidadorForm(request.POST, instance=cuidador)
        if form.is_valid():
            # Asignar latitud y longitud antes de guardar el modelo
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                latitud, longitud = ubicacion.split(',')
                cuidador.latitud = float(latitud)
                cuidador.longitud = float(longitud)
            cuidador = form.save(commit=False)  # Guardar el objeto Cuidador después de asignar la latitud y longitud
            cuidador.save()
            messages.success(request, "Sus datos han sido guardados correctamente.")
            return redirect('employee')
    else:
        form = CuidadorForm(instance=cuidador)

    response = render(request, 'cuidadores/registro_datos_cuidador.html', {'form': form})
    response.set_cookie('token', current_token, httponly=True, secure=True)
    
    return response

@login_required
def listar_datos_cuidador(request):
    try:
        # Intenta obtener los datos de propietario del usuario actual
        cuidador = Cuidador.objects.get(user=request.user)

        context = {
            'cuidador': cuidador,
        }
        return render(request, 'cuidadores/listar_datos_cuidador.html', context)
    except Cuidador.DoesNotExist:
        # Maneja el caso en el que no existen datos de propietario
        return render(request, 'cuidadores/registro_datos_cuidador.html')
    

@login_required
def editar_datos_cuidador(request):
    try:
        cuidador = Cuidador.objects.get(user=request.user)

        if request.method == 'POST':
            form = CuidadorForm(request.POST, instance=cuidador)
            if form.is_valid():
                # Asignar latitud y longitud antes de guardar el modelo
                ubicacion = request.POST.get('ubicacion', '')
                if ubicacion:
                    latitud, longitud = ubicacion.split(',')
                    cuidador.latitud = float(latitud)
                    cuidador.longitud = float(longitud)
                cuidador = form.save(commit=False)
                cuidador.save()
                messages.success(request, "Sus datos han sido actualizados correctamente.")
                return redirect('listar_datos_cuidador')  
        else:
            form = CuidadorForm(instance=cuidador)

        return render(request, 'cuidadores/editar_datos_cuidador.html', {
            'form': form,
            'cuidador': cuidador  # Pasamos el objeto cuidador para acceder a la latitud y longitud en el template
        })
    except Cuidador.DoesNotExist:
        return redirect('registrar_datos_cuidador')
    
def solicitudes_cercanas(request, cuidador_id):
    # Suponiendo que tienes un cuidador ya autenticado o lo identificas por un ID
    cuidador = Cuidador.objects.get(id=cuidador_id)
    
    # Definir un rango de búsqueda, por ejemplo 10 kilómetros.
    RANGO_BUSQUEDA = 10  # kilómetros

    # Obtener todas las solicitudes de cuidado con estado 'Pendiente'.
    solicitudes_pendientes = SolicitudDeCuidado.objects.filter(estado='Pendiente')

    # Filtrar las solicitudes que están dentro del rango del cuidador
    solicitudes_cercanas = []
    for solicitud in solicitudes_pendientes:
        if solicitud.latitud and solicitud.longitud and cuidador.latitud and cuidador.longitud:
            distancia = geodesic(
                (solicitud.latitud, solicitud.longitud),
                (cuidador.latitud, cuidador.longitud)
            ).kilometers

            if distancia <= RANGO_BUSQUEDA:
                solicitudes_cercanas.append(solicitud)

    # Ahora tienes una lista de solicitudes cercanas que puedes pasar al contexto de tu template o como JSON si estás haciendo una API
    context = {
        'solicitudes_cercanas': solicitudes_cercanas,
    }

    return render(request, 'cuidadores/solicitudes_cercanas.html', context)

#ver solicitud
def ver_solicitud(request, solicitud_id):
    # Obtener la solicitud específica y las mascotas relacionadas.
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    mascotas = solicitud.mascotas.all()  # Obtener todas las mascotas relacionadas con la solicitud

    # Pasar la solicitud y las mascotas al contexto de la plantilla.
    context = {
        'solicitud': solicitud,
        'mascotas': mascotas,
    }
    
    return render(request, 'cuidadores/solicitud_detalle.html', context)

@login_required
def registrar_datos_propietario(request):
    # Obtén el token actual del usuario autenticado
    current_token = request.COOKIES.get('token')
    from_menu = request.GET.get('from_menu')  # Verifica si el usuario viene de hacer clic en "Mascotas"

    try:
        # Intenta obtener los datos de propietario del usuario actual
        propietario = Propietario.objects.get(user=request.user)
        form = PropietarioForm(instance=propietario)
    except Propietario.DoesNotExist:
        propietario = None
        form = PropietarioForm()

    if request.method == 'POST':
        form = PropietarioForm(request.POST, instance=propietario)
        if form.is_valid():
            propietario = form.save(commit=False)
            propietario.user = request.user
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                latitud, longitud = ubicacion.split(',')
                propietario.latitud = float(latitud)
                propietario.longitud = float(longitud)
            propietario.save()
            

            # Redirige después de la creación/actualización
            if from_menu:
                messages.success(request, "Tus datos han sido registrados correctamente.")
                return redirect('listar_mascotas')
            messages.success(request, "Tus datos han sido registrados correctamente.")
            return redirect('inicio')
        
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
                # Primero guardamos el formulario
                propietario = form.save(commit=False)

                # Luego actualizamos la latitud y longitud si están presentes
                ubicacion = request.POST.get('ubicacion', '')
                if ubicacion:
                    latitud, longitud = ubicacion.split(',')
                    propietario.latitud = float(latitud)
                    propietario.longitud = float(longitud)

                # Finalmente, guardamos el objeto propietario
                propietario.save()

                messages.success(request, "Sus datos han sido actualizados correctamente.")
                return redirect('listar_datos_propietario')
        else:
            form = PropietarioForm(instance=propietario)

        context = {
            'form': form,
            'propietario': propietario,
        }
        return render(request, 'editar_datos_propietario.html', context)
    except Propietario.DoesNotExist:
        messages.error(request, "No se encontró el perfil del propietario.")
        return redirect('registrar_datos_propietario')
    

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
    if not request.user.is_customer:
        return HttpResponse('No tienes permiso para acceder a esta página.')
    
    propietario = getattr(request.user, 'propietario', None)
    if not propietario:
        messages.warning(request, 'Debes ingresar tus datos de propietario primero.')
        return redirect('registro_datos_propietario')
    
    mascotas = Mascota.objects.filter(propietario=propietario)
    return render(request, 'mascotas/listar_mascotas.html', {'mascotas': mascotas})
    
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
def publicar_paseo(request):
    if request.method == 'POST':
        form = PaseoForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.propietario = request.user.propietario
            solicitud.estado = 'Pendiente'
            
            # Intenta obtener el objeto TipoDeCuidado con el nombre 'Paseo'
            try:
                tipo_paseo, created = TipoDeCuidado.objects.get_or_create(nombre='Paseo')
            except ObjectDoesNotExist:
                messages.error(request, "No se pudo encontrar el tipo de cuidado 'Paseo'.")
                return render(request, 'cuidados/publicar_paseo.html', {'form': form})
            
            solicitud.tipo_de_cuidado = tipo_paseo
            
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
            
            messages.success(request, "La solicitud de paseo ha sido publicada con éxito.")
            return redirect('listar_solicitudes_de_cuidado')
    else:
        # Crear un objeto TipoDeCuidado llamado "Paseo" si no existe
        tipo_paseo = TipoDeCuidado.objects.get(nombre='Paseo')
        
        form = PaseoForm(initial={'tipo_de_cuidado': tipo_paseo})
        
        # Filtra las mascotas del propietario autenticado
        propietario = request.user.propietario
        form.fields['mascotas'].queryset = Mascota.objects.filter(propietario=propietario)

    return render(request, 'cuidados/publicar_paseo.html', {'form': form})

@login_required
def listar_solicitudes_de_cuidado(request):
    propietario = request.user.propietario
    solicitudes = SolicitudDeCuidado.objects.filter(propietario=propietario)
    return render(request, 'cuidados/listar_solicitudes.html', {'solicitudes': solicitudes})