from django.db import models

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
