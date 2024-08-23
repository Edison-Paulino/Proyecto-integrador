from django.shortcuts import render, redirect, get_object_or_404 
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
from .models import RangoParametro, Alerta, DatosEstacion
from datetime import datetime
from .models import Estacion 
from .forms import EstacionForm 

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
    
    # Si el promedio es 0 o no hay datos, mostramos 22
    if not promedio_temperatura or promedio_temperatura == 0:
        promedio_temperatura = 22

    estaciones = Estacion.objects.all()

    # Procesar las lecturas de la estación y verificar alertas
    datos_estacion = DatosEstacion.objects.latest('fecha')  # Ejemplo, obtén la última lectura
    verificar_alertas(datos_estacion)

    alertas_activas = Alerta.objects.filter(es_activa=True).count()  # Contar alertas activas
    # Datos para la página de inicio (Home)

    context = {
        'ciudad': 'Santiago',
        'fecha_hora': fecha_hora,
        'temperatura': round(promedio_temperatura, 0),  # Redondeamos el promedio a 2 decimales
        'estaciones': estaciones,
    }
    
    return render(request, 'home.html', context)

@login_required
def crear_estacion_view(request):
    if request.method == 'POST':
        form = EstacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirige a la página principal después de crear la estación
    else:
        form = EstacionForm()
    
    return render(request, 'crear_estacion.html', {'form': form})

@login_required
def editar_estacion_view(request, id):
    estacion = get_object_or_404(Estacion, id=id)
    if request.method == 'POST':
        form = EstacionForm(request.POST, instance=estacion)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EstacionForm(instance=estacion)
    
    return render(request, 'editar_estacion.html', {'form': form})


@login_required
def eliminar_estacion_view(request, id):
    estacion = get_object_or_404(Estacion, id=id)
    estacion.delete()
    return redirect('home')

def verificar_alertas(datos_estacion):
    # Obtener todos los parámetros definidos
    parametros = RangoParametro.objects.all()

    for parametro in parametros:
        # Obtener el valor de la estación para la variable que se está verificando
        valor_variable = getattr(datos_estacion, parametro.nombre.lower())

        # Verificar si el valor está fuera del rango permitido
        if valor_variable < parametro.limite_inferior or valor_variable > parametro.limite_superior:
            # Crear una alerta si está fuera de rango
            descripcion = f"{parametro.nombre} fuera de rango: {valor_variable}"
            Alerta.objects.create(tipo_alerta=parametro.nombre, descripcion=descripcion)

def alertas_view(request):
    alertas = Alerta.objects.filter(es_activa=True).order_by('-fecha_hora')
    return render(request, 'alertas.html', {'alertas': alertas})

def administrar_alertas_view(request):
    parametros = RangoParametro.objects.all()

    if request.method == 'POST':
        for parametro in parametros:
            limite_inferior = request.POST.get(f'limite_inferior_{parametro.id}')
            limite_superior = request.POST.get(f'limite_superior_{parametro.id}')
            parametro.limite_inferior = float(limite_inferior)
            parametro.limite_superior = float(limite_superior)
            parametro.save()
        return redirect('alertas')

    return render(request, 'administrar_alertas.html', {'parametros': parametros})

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