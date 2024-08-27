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
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Estacion 
from .forms import EstacionForm 
from django.http import HttpResponse
from .forms import ExportForm
import json
import csv
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.timezone import localtime
from datetime import timedelta
from django.utils import timezone

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

def obtener_datos(request):
    # Obtener los últimos 20 datos de la estación
    datos = DatosEstacion.objects.order_by('-fecha')[:20]
    
    # Convertir los datos a un formato que pueda ser enviado como JSON
    datos_list = []
    for dato in datos:
        datos_list.append({
            'temperatura': dato.temperatura,
            'presion': dato.presion,
            'velocidad_viento': dato.velocidad_viento,
            'direccion_viento': dato.direccion_viento,
            'humedad': dato.humedad,
            'pluvialidad': dato.pluvialidad,
            'fecha': dato.fecha,  # Convertir a la hora local
        })

    return JsonResponse(datos_list, safe=False)

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
    verificar_conexion_estacion()

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
        'alertas_activas': alertas_activas
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

    # Mapeo explícito entre los nombres de parámetros y los atributos del modelo
    mapeo_atributos = {
        'temperatura': 'temperatura',
        'presión': 'presion',
        'humedad': 'humedad',
        'lluvia': 'pluvialidad',  # Si "lluvia" se refiere a "pluvialidad"
        'dir_viento': 'direccion_viento',
        'vel_viento': 'velocidad_viento'
    }

    for parametro in parametros:
        # Mapea el nombre del parámetro al atributo correcto del modelo
        nombre_parametro = parametro.nombre.lower()
        atributo_modelo = mapeo_atributos.get(nombre_parametro)
        
        # Si el atributo existe en el modelo, procedemos
        if atributo_modelo:
            valor_variable = getattr(datos_estacion, atributo_modelo)

            # Verificar si el valor está fuera del rango permitido
            if valor_variable < parametro.limite_inferior or valor_variable > parametro.limite_superior:
                # Crear una alerta si está fuera de rango
                descripcion = f"{parametro.nombre} fuera de rango: {valor_variable}"
                Alerta.objects.create(tipo_alerta=parametro.nombre, descripcion=descripcion)

def alertas_view(request):
    alertas = Alerta.objects.filter(es_activa=True).order_by('-fecha_hora')
    return render(request, 'alertas.html', {'alertas': alertas})

@login_required
def eliminar_alerta_view(request, id):
    alerta = get_object_or_404(Alerta, id=id)
    alerta.es_activa = False
    alerta.save()
    return redirect('alertas')  # Redirige de nuevo a la página de alertas


def verificar_conexion_estacion():
    # Obtener la última lectura
    ultima_lectura = DatosEstacion.objects.order_by('-fecha').first()
    
    if ultima_lectura:
        tiempo_actual = timezone.now() + timedelta(hours=4)  # Sumar 4 horas al tiempo actual
        tiempo_lectura = ultima_lectura.fecha

        # Si han pasado más de 2 minutos desde la última lectura
        if tiempo_actual - tiempo_lectura > timedelta(minutes=2):
            # Verificar si ya existe una alerta de desconexión
            if not Alerta.objects.filter(tipo_alerta="Desconexión", es_activa=True).exists():
                Alerta.objects.create(
                    tipo_alerta="Desconexión",
                    descripcion="La estación no está enviando datos desde hace más de 2 minutos",
                    es_activa=True
                )
        else:
            # Si los datos han vuelto a recibirse, marcar la estación como conectada
            alertas_desconexion = Alerta.objects.filter(tipo_alerta="Desconexión", es_activa=True)
            if alertas_desconexion.exists():
                alertas_desconexion.update(es_activa=False)
                Alerta.objects.create(
                    tipo_alerta="Conexión",
                    descripcion="La estación ha vuelto a conectarse y está enviando datos",
                    es_activa=True
                )

def administrar_alertas_view(request):
    # Verifica si ya existen parámetros
    parametros = RangoParametro.objects.all()

    # Si no hay parámetros, permitir agregar nuevos
    if not parametros.exists():
        if request.method == 'POST':
            # Crear parámetros por defecto (ejemplo para seis variables)
            nombres = ['Temperatura', 'Presión', 'Humedad', 'LLuvia', 'Dir_Viento', 'Vel_Viento']
            for nombre in nombres:
                limite_inferior = request.POST.get(f'limite_inferior_{nombre}')
                limite_superior = request.POST.get(f'limite_superior_{nombre}')
                RangoParametro.objects.create(
                    nombre=nombre,
                    limite_inferior=float(limite_inferior),
                    limite_superior=float(limite_superior)
                )
            return redirect('alertas')  # Redirigir después de guardar
        return render(request, 'administrar_alertas.html', {'nuevos_parametros': True})

    # Si ya hay parámetros, permitir modificarlos
    else:
        if request.method == 'POST':
            for parametro in parametros:
                limite_inferior = request.POST.get(f'limite_inferior_{parametro.id}')
                limite_superior = request.POST.get(f'limite_superior_{parametro.id}')
                parametro.limite_inferior = float(limite_inferior)
                parametro.limite_superior = float(limite_superior)
                parametro.save()
            return redirect('alertas')  # Redirigir después de guardar
        return render(request, 'administrar_alertas.html', {'parametros': parametros})

@login_required
def exportar_view(request):
    estaciones = Estacion.objects.all()  # Obtener todas las estaciones

    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
            estacion = form.cleaned_data['estacion']
            sensor = form.cleaned_data['sensor']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            hora_inicio = form.cleaned_data['hora_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            hora_fin = form.cleaned_data['hora_fin']
            formato = form.cleaned_data['formato']

            # Combinar fecha y hora en un solo datetime
            fecha_hora_inicio = datetime.combine(fecha_inicio, hora_inicio)
            fecha_hora_fin = datetime.combine(fecha_fin, hora_fin)

            # Filtrar los datos según la estación, sensor y rango de fechas
            datos = DatosEstacion.objects.filter(
                fecha__range=(fecha_hora_inicio, fecha_hora_fin)
            )
            
            if estacion != 'TODAS':
                datos = datos.filter(estacion__id=estacion)
            
            if sensor != 'TODOS':
                datos = datos.only(sensor)  # Filtrar solo por el sensor seleccionado

            # Exportar según el formato seleccionado
            if formato == 'JSON':
                return exportar_json(datos)
            elif formato == 'CSV':
                return exportar_csv(datos)

    else:
        form = ExportForm()

    return render(request, 'exportar.html', {'form': form, 'estaciones': estaciones})

def exportar_json(datos):
    # Convertimos cada objeto de datos en un diccionario y formateamos el campo de fecha
    data = []
    for dato in datos:
        data.append({
            'fecha': dato.fecha.strftime("%Y-%m-%d %H:%M:%S"),  # Convertimos datetime a cadena
            'temperatura': dato.temperatura,
            'presion': dato.presion,
            'humedad': dato.humedad,
            'velocidad_viento': dato.velocidad_viento,
            'direccion_viento': dato.direccion_viento,
            'pluvialidad': dato.pluvialidad
        })

    response = HttpResponse(json.dumps(data, indent=4), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="datos_estacion.json"'
    return response


def exportar_csv(datos):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="datos_estacion.csv"'
    writer = csv.writer(response)
    
    # Si existen datos, escribimos los encabezados de las columnas
    if datos.exists():
        primer_dato = datos.first()
        # Extraer los nombres de los campos de la clase DatosEstacion
        campos = ['fecha', 'temperatura', 'presion', 'humedad', 'velocidad_viento', 'direccion_viento', 'pluvialidad']
        writer.writerow(campos)
        
        # Escribir los valores de los datos
        for dato in datos:
            writer.writerow([getattr(dato, campo) for campo in campos])

    return response


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