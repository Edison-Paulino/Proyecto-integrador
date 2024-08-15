from django.db import models

# Create your models here.

class DatoEstacion(models.Model):
    id_estacion = models.IntegerField()
    fecha = models.DateTimeField()
    temperatura = models.FloatField()
    humedad = models.FloatField()
    presion = models.FloatField()
    velocidad_viento = models.FloatField()
    direccion_viento = models.FloatField()
    pluvialidad = models.FloatField()

    def __str__(self):
        return f"Estación {self.id_estacion} - Fecha: {self.fecha}"