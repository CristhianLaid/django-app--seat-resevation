from django.db import models
from django.contrib.auth.models import User
from apps.security.models import ModelBase

class Sensor(ModelBase):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    estado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        unique_together = ['nombre', 'ubicacion']

    def __str__(self):
        return self.nombre

class Reservacion(ModelBase):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_reservacion = models.DateTimeField()
    sensor_activado = models.OneToOneField(Sensor, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservacion {self.id} - {self.fecha_reservacion}"
