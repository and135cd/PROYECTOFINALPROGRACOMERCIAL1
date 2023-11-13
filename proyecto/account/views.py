from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from account.models import User
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.mail import send_mail
from django.http import HttpResponse  
from geopy.distance import geodesic
import jwt  
from django.contrib.auth.decorators import login_required
from .forms import PropietarioForm, MascotaForm, AlojamientoForm, CuidadorForm, PaseoForm, ContactForm, GuarderiaForm, PeluqueriaForm, SolicitudDeCuidadoForm, UserForm
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


@login_required
def inicio(request):
    try:
        # Supongamos que tienes la latitud y longitud del propietario
        propietario = Propietario.objects.get(user=request.user)
        propietario_location = (propietario.latitud, propietario.longitud)

        # Obtener todos los cuidadores (en un sistema real, probablemente querrás limitar esto)
        todos_los_cuidadores = Cuidador.objects.all()

        # Calcula la distancia y filtra los cuidadores dentro de un radio de 10 kilómetros
        cuidadores_cercanos = []
        for cuidador in todos_los_cuidadores:
            cuidador_location = (cuidador.latitud, cuidador.longitud)
            distance = geodesic(propietario_location, cuidador_location).km
            if distance <= 3:  # Cambia 5 por la distancia que consideres 'cercana'
                cuidador.distance = distance
                cuidadores_cercanos.append(cuidador)

        # Ordena por la distancia calculada
        cuidadores_cercanos.sort(key=lambda x: x.distance)

        return render(request, 'inicio.html', {'cuidadores_cercanos': cuidadores_cercanos})
    except ObjectDoesNotExist:
        return render(request, 'inicio.html')

def employee_inicio(request):
    # Obtener la fecha actual
    hoy = timezone.now().date()
    cuidador=request.user.cuidador
    # Encuentra las solicitudes de cuidado para el día actual
    solicitudes_hoy = SolicitudDeCuidado.objects.filter(
        fecha_inicio=hoy, 
        cuidadores_aceptan=cuidador
    ).order_by('hora_inicio')
    
    # Si hay solicitudes para hoy, toma la primera para el recordatorio
    proxima_cita = solicitudes_hoy.first() if solicitudes_hoy else None

    return render(request, 'cuidadores/inicio_employee.html', {
        'proxima_cita': proxima_cita,
    })

def contactar_cuidador(request, cuidador_id):
    cuidador = get_object_or_404(Cuidador, pk=cuidador_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['email']
            recipients = [cuidador.user.email] 
            
            send_mail(subject, message+ "\nmensaje de parte de: "+request.user.email, sender, recipients)
            messages.success(request,"Mensaje enviado a cuidador")
            return redirect('inicio')
    else:
        form = ContactForm(initial={'email': cuidador.user.email})

    return render(request, 'cuidadores/contactar_cuidador.html', {'cuidador': cuidador, 'form': form})

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
                    response = redirect('inicio') 
                    response.set_cookie('token', token, httponly=True, secure=True)  
                    return response
                elif user.is_employee:
                    response = render(request, 'cuidadores/inicio_employee.html',context) 
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
        cuidador = get_object_or_404(Cuidador, user=request.user)
        user = request.user

        if request.method == 'POST':
            cuidador_form = CuidadorForm(request.POST, instance=cuidador)
            user_form = UserForm(request.POST, instance=user)

            if cuidador_form.is_valid() and user_form.is_valid():
                # Guardar UserForm
                user_form.save()
                
                # Procesar CuidadorForm
                cuidador = cuidador_form.save(commit=False)
                # ... procesar los campos de Cuidador como la latitud y longitud
                cuidador.save()

                messages.success(request, "Sus datos han sido actualizados correctamente.")
                return redirect('listar_datos_cuidador')
        else:
            cuidador_form = CuidadorForm(instance=cuidador)
            user_form = UserForm(instance=user)

        return render(request, 'cuidadores/editar_datos_cuidador.html', {
            'cuidador_form': cuidador_form,
            'user_form': user_form,
            'cuidador': cuidador
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

#ver solicitud aceptada
def ver_solicitud_aceptada(request, solicitud_id):
    # Obtener la solicitud específica y las mascotas relacionadas.
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    mascotas = solicitud.mascotas.all()  # Obtener todas las mascotas relacionadas con la solicitud

    # Pasar la solicitud y las mascotas al contexto de la plantilla.
    context = {
        'solicitud': solicitud,
        'mascotas': mascotas,
    }
    
    return render(request, 'cuidadores/solicitud_detalle_aceptada.html', context)

def ver_solicitud_cliente(request, solicitud_id):
    # Obtener la solicitud específica y las mascotas relacionadas.
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    mascotas = solicitud.mascotas.all()  # Obtener todas las mascotas relacionadas con la solicitud

    # Pasar la solicitud y las mascotas al contexto de la plantilla.
    context = {
        'solicitud': solicitud,
        'mascotas': mascotas,
    }
    
    return render(request, 'clientes/detalle_solicitud.html', context)


@login_required
def editar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id, propietario=request.user.propietario)
    if request.method == 'POST':
        form = SolicitudDeCuidadoForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request,'Solicitud actualizada')
            return redirect('listar_solicitudes_de_cuidado')
    else:
        form = SolicitudDeCuidadoForm(instance=solicitud)
        form.fields['mascotas'].queryset=Mascota.objects.filter(propietario=request.user.propietario)
    return render(request, 'clientes/editar_solicitud.html', {'form': form})


@login_required
def eliminar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    
    if solicitud.propietario.user != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta solicitud.")

    if request.method == 'POST':
        solicitud.delete()
        messages.success(request, 'La solicitud de cuidado ha sido eliminada.')
        return redirect('listar_solicitudes_de_cuidado')  
    
    return render(request, 'clientes/eliminar_solicitud.html', {'solicitud': solicitud})
@login_required
def aceptar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    
    if request.user.is_employee:  
        if solicitud.estado not in ['Aceptada', 'Rechazada']:  # Comprueba que la solicitud no haya sido ya aceptada o rechazada
            solicitud.aceptar(request.user.cuidador)  # Llama al método aceptar
            # Aquí se envia un correo
            subject = "Tu solicitud de cuidado ha sido aceptada"
            message = f"Hola {solicitud.propietario.nombre},\n\n" \
                    f"Tu solicitud de cuidado para la fecha {solicitud.fecha_inicio} ha sido aceptada por {request.user.get_full_name()}.\n" \
                    "Pronto se pondrán en contacto contigo para más detalles."
            email_from = request.user.email
            recipient_list = [solicitud.propietario.user.email]
            
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Has aceptado la solicitud.")
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
        else:
            messages.warning(request, "Esta solicitud ya ha sido respondida.")
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    else:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción")
    

@login_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudDeCuidado, id=solicitud_id)
    
    if request.user.is_employee:  
        if solicitud.estado not in ['Aceptada', 'Rechazada']:  # Verifica que la solicitud no ha sido previamente aceptada o rechazada
            solicitud.rechazar(request.user.cuidador)  # Llama al método rechazar
            # Aquí se envia un correo
            subject = "Notificación de rechazo de solicitud de cuidado"
            message = f"Hola {solicitud.propietario.nombre},\n\nLamentamos informarte que tu solicitud de cuidado número {solicitud_id} ha sido rechazada por el cuidador. Te invitamos a ver otros cuidadores disponibles en nuestra plataforma.\n\nSaludos,\nEquipo Huellitas"
            email_from = request.user.email
            recipient_list = [solicitud.propietario.user.email]
            
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, "Has rechazado la solicitud.")
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
        else:
            messages.warning(request, "Esta solicitud ya ha sido respondida.")
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    else:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción")

@login_required
def ver_solicitudes_aceptadas(request):
    # Asegúrate de que el usuario es un cuidador
    if not request.user.is_employee:
        return HttpResponse('No tienes permiso para acceder a esta página.')

    cuidador = request.user.cuidador
    # Filtra las solicitudes de cuidado que han sido aceptadas por este cuidador
    solicitudes_aceptadas = SolicitudDeCuidado.objects.filter(cuidadores_aceptan=cuidador, estado='Aceptada')
    
    return render(request, 'cuidadores/solicitudes_aceptadas.html', {'solicitudes_aceptadas': solicitudes_aceptadas})

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
    propietario = get_object_or_404(Propietario, user=request.user)
    user_form = UserForm(instance=request.user)
    propietario_form = PropietarioForm(instance=propietario)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        propietario_form = PropietarioForm(request.POST, request.FILES, instance=propietario)
        if user_form.is_valid() and propietario_form.is_valid():
            user = user_form.save(commit=False)
            propietario = propietario_form.save(commit=False)
            
            # Actualizamos la latitud y longitud si están presentes
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                latitud, longitud = ubicacion.split(',')
                propietario.latitud = float(latitud)
                propietario.longitud = float(longitud)
            
            user.save()
            propietario.save()
            messages.success(request, "Sus datos han sido actualizados correctamente.")
            return redirect('listar_datos_propietario')
    else:
        user_form = UserForm(instance=request.user)
        propietario_form = PropietarioForm(instance=propietario)

    context = {
        'user_form': user_form,
        'propietario_form': propietario_form,
        'propietario': propietario,  
    }
    return render(request, 'editar_datos_propietario.html', context)
    

def customer(request):
    # Obtener el token actual del usuario autenticado
    current_token = request.COOKIES.get('token')
    # Verificar si el usuario autenticado ya tiene un propietario asociado
    try:
        propietario = Propietario.objects.get(user_id=request.user.id)
        propietario_nombre = f"{propietario.nombre} {propietario.apellido}"
    except Propietario.DoesNotExist:
        propietario_nombre = None

    context = {
        'user': request.user,
        'propietario_nombre': propietario_nombre,
    }
    # Renderizar la página de customer y establecer el token en la cookie
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
    if mascota.propietario != request.propietario.user:
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
            solicitud.calcular_precio()    
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
                tipo_paseo = TipoDeCuidado.objects.get(nombre='Paseo')
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
                
          
            if 'fecha_fin' not in request.POST or not request.POST['fecha_fin']:
                solicitud.fecha_fin = None

            solicitud.calcular_precio()    
            solicitud.save()
            form.save_m2m()  
            
            messages.success(request, "La solicitud de paseo ha sido publicada con éxito.")
            return redirect('listar_solicitudes_de_cuidado')
    else:
        
        tipo_paseo = TipoDeCuidado.objects.get(nombre='Paseo')
        
        form = PaseoForm(initial={'tipo_de_cuidado': tipo_paseo})
        
        
        propietario = request.user.propietario
        form.fields['mascotas'].queryset = Mascota.objects.filter(propietario=propietario)

    return render(request, 'cuidados/publicar_paseo.html', {'form': form})

@login_required
def publicar_guarderia(request):
    if request.method == 'POST':
        form = GuarderiaForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.propietario = request.user.propietario
            solicitud.estado = 'Pendiente'
            
            # Intenta obtener el objeto TipoDeCuidado con el nombre 'Guarderia'
            try:
                tipo_guarderia = TipoDeCuidado.objects.get(nombre='Guarderia')
            except ObjectDoesNotExist:
                messages.warning(request, "No se pudo encontrar el tipo de cuidado 'Guarderia'.")
                return render(request, 'cuidados/publicar_guarderia.html', {'form': form})
            
            solicitud.tipo_cuidado = tipo_guarderia
            
            # Obtiene las coordenadas de la ubicación desde el formulario
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                try:
                    lat, lng = map(float, ubicacion.split(','))
                    solicitud.latitud = lat
                    solicitud.longitud = lng
                except ValueError:
                    messages.error(request, "La ubicación proporcionada es inválida.")
                    return render(request, 'cuidados/publicar_guarderia.html', {'form': form})
            solicitud.calcular_precio()    
            solicitud.save()
            form.save_m2m()  
            
            messages.success(request, "La solicitud de guarderia ha sido publicada con éxito.")
            return redirect('listar_solicitudes_de_cuidado')
    else:
        
        tipo_guarderia = TipoDeCuidado.objects.get(nombre='Guarderia')
        
        form = GuarderiaForm(initial={'tipo_de_cuidado': tipo_guarderia})
        
        
        propietario = request.user.propietario
        form.fields['mascotas'].queryset = Mascota.objects.filter(propietario=propietario)

    return render(request, 'cuidados/publicar_guarderia.html', {'form': form})

@login_required
def publicar_peluqueria(request):
    if request.method == 'POST':
        form = PeluqueriaForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.propietario = request.user.propietario
            solicitud.estado = 'Pendiente'
            
            # Intenta obtener el objeto TipoDeCuidado con el nombre 'Peluqueria'
            try:
                tipo_peluqueria = TipoDeCuidado.objects.get(nombre='Peluqueria')
            except ObjectDoesNotExist:
                messages.error(request, "No se pudo encontrar el tipo de cuidado 'Peluqueria'.")
                return render(request, 'cuidados/publicar_peluqueria.html', {'form': form})
            
            solicitud.tipo_de_cuidado = tipo_peluqueria
            
            # Obtiene las coordenadas de la ubicación desde el formulario
            ubicacion = request.POST.get('ubicacion', '')
            if ubicacion:
                try:
                    lat, lng = map(float, ubicacion.split(','))
                    solicitud.latitud = lat
                    solicitud.longitud = lng
                except ValueError:
                    messages.error(request, "La ubicación proporcionada es inválida.")
                    return render(request, 'cuidados/publicar_peluqueria.html', {'form': form})
            solicitud.calcular_precio()    
            solicitud.save()
            form.save_m2m()  
            
            messages.success(request, "La solicitud de peluqueria ha sido publicada con éxito.")
            return redirect('listar_solicitudes_de_cuidado')
    else:
        
        tipo_peluqueria = TipoDeCuidado.objects.get(nombre='Peluqueria')
        
        form = PeluqueriaForm(initial={'tipo_de_cuidado': tipo_peluqueria})
        
        
        propietario = request.user.propietario
        form.fields['mascotas'].queryset = Mascota.objects.filter(propietario=propietario)

    return render(request, 'cuidados/publicar_peluqueria.html', {'form': form})


@login_required
def listar_solicitudes_de_cuidado(request):
    propietario = request.user.propietario
    solicitudes = SolicitudDeCuidado.objects.filter(propietario=propietario)
    return render(request, 'cuidados/listar_solicitudes.html', {'solicitudes': solicitudes})