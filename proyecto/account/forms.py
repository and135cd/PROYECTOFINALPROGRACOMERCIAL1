# forms.py
from django import forms
from .models import Propietario, Mascota

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido','direccion', 'telefono' ]  # Ajusta los campos según tus necesidades

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre','especie','genero','raza','edad']