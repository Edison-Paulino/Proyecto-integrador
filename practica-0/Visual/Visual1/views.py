
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import DatosEstacion

def datos_estacion(request):
    datos = DatosEstacion.objects.all().order_by('-Fecha')
    paginator = Paginator(datos, 10)  # Mostrar 10 elementos por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'visual1/datos_estacion.html', {'page_obj': page_obj})
