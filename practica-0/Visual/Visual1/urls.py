
from django.urls import path
from .views import datos_estacion, login_view, register_view, dashboard_view
from .views import alerts_view, export_view, logout_view

urlpatterns = [
    path('datos/', datos_estacion, name='datos_estacion'),
    path('login/', login_view, name='login'),          # Ruta para el login
    path('register/', register_view, name='register'),  # Ruta para el registro
    path('dashboard/', dashboard_view, name='dashboard'),  # Ruta para el dashboard
    path('alerts/', alerts_view, name='alerts'),       # Ruta para las alertas
    path('export/', export_view, name='export'),       # Ruta para la exportación
    path('logout/', logout_view, name='logout'),       # Ruta para el logout
]
