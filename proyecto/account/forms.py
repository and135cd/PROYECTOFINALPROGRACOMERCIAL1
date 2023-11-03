# forms.py
from django import forms
from .models import Propietario, Mascota, SolicitudDeCuidado, TipoDeCuidado, Cuidador

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['nombre', 'apellido','direccion', 'telefono' ]   

class CuidadorForm(forms.ModelForm):
    class Meta:
        model = Cuidador
        fields = ['nombre', 'apellido','direccion', 'telefono' ]  
        
class MascotaForm(forms.ModelForm):
    edad = forms.IntegerField(label='Edad en años')
    class Meta:
        model = Mascota
        fields = ['nombre','especie','genero','raza','edad']
    
class AlojamientoForm(forms.ModelForm):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora_inicio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    hora_fin = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_solicitud = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)  # Agrega el campo fecha_solicitud
    ubicacion_servicio = forms.CharField(max_length=200)  # Campo de ubicación
    mascotas = forms.ModelMultipleChoiceField(
        queryset=Mascota.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Mascotas',
        required=False,
    )
    # Cambia tipo_de_cuidado a ModelChoiceField y obtén el tipo correcto en la vista.
    tipo_de_cuidado = forms.ModelChoiceField(
        queryset=TipoDeCuidado.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=False  # Siempre estableceremos esto en la vista, no necesita ser enviado por el formulario
    )

    class Meta:
        model = SolicitudDeCuidado
        fields = ['fecha_solicitud', 'fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin', 'ubicacion_servicio', 'descripcion', 'mascotas','tipo_de_cuidado']

class PaseoForm(forms.ModelForm):
    fecha_solicitud = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False  
    )
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora_inicio = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    hora_fin = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    ubicacion_servicio = forms.CharField(max_length=200)
    mascotas = forms.ModelMultipleChoiceField(
        queryset=Mascota.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Mascotas',
        required=True,
    )
    descripcion = forms.CharField(widget=forms.Textarea)
    # Cambia tipo_de_cuidado a ModelChoiceField y obtén el tipo correcto en la vista.
    tipo_de_cuidado = forms.ModelChoiceField(
        queryset=TipoDeCuidado.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=False  # Siempre estableceremos esto en la vista, no necesita ser enviado por el formulario
    )

    class Meta:
        model = SolicitudDeCuidado
        fields = [
            'fecha_solicitud', 'fecha_inicio', 'hora_inicio', 
            'hora_fin', 'ubicacion_servicio', 'descripcion', 
            'tipo_de_cuidado', 'mascotas',
        ]
        exclude = ['fecha_fin']  # Excluimos solo fecha_fin del formulario