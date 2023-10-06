# forms.py
from django import forms
from .models import Propietario, Mascota, SolicitudDeCuidado

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido','direccion', 'telefono' ]  # Ajusta los campos según tus necesidades

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre','especie','genero','raza','edad']
    
class AlojamientoForm(forms.ModelForm):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_solicitud = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)  # Agrega el campo fecha_solicitud
    ubicacion_servicio = forms.CharField(max_length=200)  # Campo de ubicación
    mascotas = forms.ModelMultipleChoiceField(
        queryset=Mascota.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Mascotas',
        required=False,
    )

    class Meta:
        model = SolicitudDeCuidado
        fields = ['fecha_solicitud', 'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin', 'ubicacion_servicio', 'descripcion', 'mascotas','tipo_de_cuidado']

    