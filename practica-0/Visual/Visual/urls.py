from django.contrib import admin
from django.urls import path, include
from Visual1 import views as visual1_views  # Importa las vistas de Visual1

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', visual1_views.datos_estacion, name='datos_estacion'),  # Ruta para la URL raíz
    path('datos/', include('Visual1.urls')),
]
