from django.db import models

class DatosEstacion(models.Model):
    IdEstacion = models.IntegerField()
    Temperatura = models.FloatField()
    Presion = models.FloatField()
    Velocidad_Viento = models.FloatField()
    Direccion_Viento = models.FloatField()
    Humedad = models.FloatField()
    Pluvialidad = models.FloatField()
    Fecha = models.CharField(max_length=30, null=True)

    class Meta:
        db_table = 'datos_estacion'  # Especifica el nombre de la tabla existente
        verbose_name = 'Datos de Estación'
        verbose_name_plural = 'Datos de Estaciones'

    def __str__(self):
        return f"Estación {self.IdEstacion} - Fecha {self.Fecha}"

