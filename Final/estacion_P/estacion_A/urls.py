from django.urls import path
from . import views  # Importar las vistas desde el archivo views.py

urlpatterns = [
   path('', views.login_view, name='login'),  # Página principal redirige a login
]
