from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from account.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

# Create your views here.
def index(request):
    return render(request,'index.html')


def registro(request):
    if request.method == 'POST':
        # Define el formulario personalizado directamente en la vista
        form = forms.Form(request.POST)
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('customer', 'Usuario'), ('employee', 'Cuidador')], required=True)

        if form.is_valid():
            # Procesa el formulario aquí
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user_type = form.cleaned_data['user_type']
            # Crea el usuario en la base de datos y establece is_customer a True
            user = User.objects.create_user(username=username, email=email, password=password)
            if user_type == 'customer':
                user.is_customer = True
            elif user_type == 'employee':
                user.is_employee = True
            user.save()
            return redirect('login')
    else:
        # Define el formulario personalizado directamente en la vista
        form = forms.Form()
        form.fields['username'] = forms.CharField(max_length=150, required=True)
        form.fields['email'] = forms.EmailField(max_length=254, required=True)
        form.fields['password1'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['password2'] = forms.CharField(widget=forms.PasswordInput, required=True)
        form.fields['user_type'] = forms.ChoiceField(choices=[('customer', 'Usuario'), ('employee', 'Cuidador')], required=True)
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
                if user.is_admin:
                    return redirect('admin', {'token': user.get_token()})
                elif user.is_customer:
                    return redirect('home', {'token': user.get_token()})
                elif user.is_employee:
                    return render(request,'employee.html')
                else:
                    return render(request, 'login.html', {'error': 'nombre de usuario o correo inválidos'})
    else:
        return render(request, 'login.html')

def logout(request):
    logout(request)
    return redirect('login')

def employee(request):
    return render(request, "employee.html")