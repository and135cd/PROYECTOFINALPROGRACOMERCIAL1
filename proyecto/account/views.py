from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
def registro(request):
    model = User
    template_name = 'registro.html'
    fields = ['username', 'email', 'password1', 'password2']

    def form_valid(self, form):
        form.instance.is_customer = True
        form.save()
        return redirect('login')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        return render(request, template_name, {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to different views based on the user's role
            if user.is_admin:
                return redirect('admin', {'token': user.get_token()})
            elif user.is_customer:
                return redirect('home', {'token': user.get_token()})
            else:
                return redirect('employee', {'token': user.get_token()})
        else:
            return render(request, 'login.html', {'error': 'nombre de usuario o correo invalidos'})
    else:
        return render(request, 'login.html')

def logout(request):
    logout(request)
    return redirect('login')