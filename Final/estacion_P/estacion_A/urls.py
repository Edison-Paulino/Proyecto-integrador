from django.urls import path
from . import views  # Importar las vistas desde el archivo views.py

urlpatterns = [
   path('', views.login_view, name='login'),  # Página principal redirige a login
   path('login/', views.login_view, name='login'),  # Nueva ruta para /login/
   path('register/', views.register_view, name='register'),
]
