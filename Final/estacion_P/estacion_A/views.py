from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .models import DatosEstacion
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, CustomPasswordChangeForm
from datetime import datetime
from django.db.models import Avg
from .models import DatosEstacion 

def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la página principal después de iniciar sesión
        else:
            error_message = "Nombre de usuario o contraseña incorrectos"

    return render(request, 'login.html', {'error_message': error_message})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Autenticar y loguear automáticamente
            user = authenticate(request, username=user.username, password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
        else:
            return render(request, 'register.html', {'form': form})
    
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
            return redirect('profile')  # Redirige al perfil actualizado
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'password_form': password_form
    })

@login_required
def home_view(request):
    # Obteniendo la fecha y hora actual
    now = datetime.now()
    fecha_hora = now.strftime("%d/%m/%Y %I:%M %p")
    
    # Obtener el promedio de las últimas 20 lecturas de temperatura
    ultimas_lecturas = DatosEstacion.objects.order_by('-fecha')[:20]
    promedio_temperatura = ultimas_lecturas.aggregate(Avg('temperatura'))['temperatura__avg']
    
    # Si no hay lecturas, asigna un valor predeterminado de 0
    if promedio_temperatura is None:
        promedio_temperatura = 0

    context = {
        'ciudad': 'Santiago',
        'fecha_hora': fecha_hora,
        'temperatura': round(promedio_temperatura, 0),  # Redondeamos el promedio a 2 decimales
    }
    
    return render(request, 'home.html', context)

@login_required 
def panel_view(request):
     # Obtener el valor de registros por página del formulario, con un valor predeterminado de 10
    registros_por_pagina = request.GET.get('registros', 10)
    
    # Obtener todos los datos de la tabla DatosEstacion
    datos = DatosEstacion.objects.all().order_by('-fecha') 
    
    # Crear el paginador con el número de registros elegidos por el usuario
    paginator = Paginator(datos, registros_por_pagina)
    
    # Obtener el número de página actual
    page_number = request.GET.get('page')
    
    # Obtener los datos correspondientes a la página actual
    page_obj = paginator.get_page(page_number)
    
    # Pasar los datos paginados a la plantilla
    return render(request, 'gen_me.html', {'page_obj': page_obj, 'registros_por_pagina': registros_por_pagina})

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige al login después de cerrar sesión