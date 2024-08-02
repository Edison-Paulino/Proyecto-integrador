from django.db import models

class Estacion(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'estacion'
        verbose_name = 'Estación'
        verbose_name_plural = 'Estaciones'

    def __str__(self):
        return self.nombre

class DatosEstacion(models.Model):
    IdEstacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
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
        return f"Estación {self.IdEstacion.nombre} - Fecha {self.Fecha}"
