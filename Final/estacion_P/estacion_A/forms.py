from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Estacion

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username




class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))



class EstacionForm(forms.ModelForm):
    class Meta:
        model = Estacion
        fields = ['nombre', 'descripcion']

class ExportForm(forms.Form):
    ESTACION_CHOICES = [('TODAS', 'TODAS')] + [(estacion.nombre, estacion.nombre) for estacion in Estacion.objects.all()]
    SENSOR_CHOICES = [('TODOS', 'TODOS'), ('Temperatura', 'Temperatura'), ('Presión', 'Presion'), ('Humedad', 'Humedad'), ('Vel_Viento', 'Velocidad Viento'), ('Dir_Viento', 'Dirección Viento')]
    FORMATO_CHOICES = [('PDF', 'PDF'), ('JSON', 'JSON'), ('CSV', 'CSV')]

    estacion = forms.ChoiceField(choices=ESTACION_CHOICES)
    sensor = forms.ChoiceField(choices=SENSOR_CHOICES)
    fecha_inicio = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY'}))
    hora_inicio = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    fecha_fin = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY'}))
    hora_fin = forms.TimeField(widget=forms.TextInput(attrs={'placeholder': 'HH:MM'}))
    formato = forms.ChoiceField(choices=FORMATO_CHOICES)