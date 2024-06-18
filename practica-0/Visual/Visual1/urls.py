
from django.urls import path
from .views import datos_estacion

urlpatterns = [
    path('datos/', datos_estacion, name='datos_estacion'),
]
