from django.db import models
from django.utils import timezone

class DatosEstacion(models.Model):
    id_estacion = models.IntegerField(db_column='IdEstacion', primary_key=True)  # Nombre de la columna en la tabla
    fecha = models.DateTimeField(db_column='Fecha')
    temperatura = models.FloatField(db_column='Temperatura')
    humedad = models.FloatField(db_column='Humedad')
    presion = models.FloatField(db_column='Presion')
    velocidad_viento = models.FloatField(db_column='Velocidad_Viento')
    direccion_viento = models.FloatField(db_column='Direccion_Viento')
    pluvialidad = models.FloatField(db_column='Pluvialidad')

    class Meta:
        db_table = 'datos_estacion'  # Aquí especificamos que use la tabla existente

    def __str__(self):
        return f"Estación {self.id_estacion} - Fecha: {self.fecha}"

class Estacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        db_table = 'estacion_A_estacion'  

    def __str__(self):
        return self.nombre
    
class RangoParametro(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre de la variable (e.g. Temperatura, Presión)
    limite_inferior = models.FloatField()
    limite_superior = models.FloatField()

    class Meta:
        db_table = 'estacion_A_rangoparametro'  # Nombre exacto de la tabla en la BD

    def __str__(self):
        return self.nombre

class Alerta(models.Model):
    tipo_alerta = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField(default=timezone.now)
    es_activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'estacion_A_alerta'  # Nombre exacto de la tabla en la BD

    def __str__(self):
        return f"{self.tipo_alerta} - {self.fecha_hora}"