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
   path('gen_me/', views.panel_view, name='gen_me'),
   path('crear_estacion/', views.crear_estacion_view, name='crear_estacion'),
   path('eliminar_estacion/<int:id>/', views.eliminar_estacion_view, name='eliminar_estacion'),  # Eliminar
   path('editar_estacion/<int:id>/', views.editar_estacion_view, name='editar_estacion'),  # Editar
   path('alertas/', views.alertas_view, name='alertas'),
   path('administrar_alertas/', views.administrar_alertas_view, name='administrar_alertas'),
   path('eliminar-alerta/<int:id>/', views.eliminar_alerta_view, name='eliminar_alerta'),
] 
