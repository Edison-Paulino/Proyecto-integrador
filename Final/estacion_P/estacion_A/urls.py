from django.urls import path
from . import views  # Importar las vistas desde el archivo views.py

urlpatterns = [
   path('', views.login_view, name='login'),  # Página principal redirige a login
   path('login/', views.login_view, name='login'),  # Nueva ruta para /login/
   path('register/', views.register_view, name='register'),
   path('panel/', views.panel_view, name='panel'),
   path('logout/', views.logout_view, name='logout'),
   path('perfil/', views.profile_view, name='profile'),
   path('perfil/editar/', views.edit_profile_view, name='edit_profile'),
   path('inicio/', views.home_view, name='home'),
]
