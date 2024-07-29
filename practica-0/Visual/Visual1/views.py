from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from .models import DatosEstacion
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.decorators import login_required

def datos_estacion(request):
    datos = DatosEstacion.objects.all().order_by('-Fecha')
    paginator = Paginator(datos, 10)  # Mostrar 10 elementos por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'visual1/datos_estacion.html', {'page_obj': page_obj})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirigir a la vista de dashboard
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos')
    return render(request, 'visual1/index.html')


# Formulario de registro
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'visual1/register.html', {'form': form})


@login_required
def dashboard_view(request):
    # Aquí podrías obtener datos de estaciones y alertas desde la base de datos
    # Por ejemplo, stations = Station.objects.all() para obtener todas las estaciones
    context = {
        'stations': [],  # Reemplaza con la lista de estaciones
        'alerts': True,  # Lógica para determinar si hay alertas no leídas
    }
    return render(request, 'visual1/dashboard.html', context)


@login_required
def profile_view(request):
    return render(request, 'visual1/profile.html')

@login_required
def alerts_view(request):
    return render(request, 'visual1/alerts.html', {'alerts': []})


@login_required
def export_view(request):
    return render(request, 'visual1/export.html')


def logout_view(request):
    logout(request)
    return redirect('login')
