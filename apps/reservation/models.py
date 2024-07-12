from django.db import models
from django.core.exceptions import ValidationError

from apps.security.models import ModelBase, User

class SensorManager(models.Manager):
    def activos(self):
        try:
            return self.filter(estado=True)
        except Exception as e:
            raise ValidationError(f"Error al obtener sensores activos: {str(e)}")
    
    def inactivos(self):
        try:
            return self.filter(estado=False)
        except Exception as e:
            raise ValidationError(f"Error al obtener sensores inactivos: {str(e)}")
    
    def contar_activos(self):
        try:
            return self.filter(estado=True).count()
        except Exception as e:
            raise ValidationError(f"Error al contar sensores activos: {str(e)}")
    
    def contar_inactivos(self):
        try:
            return self.filter(estado=False).count()
        except Exception as e:
            raise ValidationError(f"Error al contar sensores inactivos: {str(e)}")
    
    def por_rango_de_fechas(self, fecha_inicio, fecha_fin):
        try:
            return self.filter(fecha_reservacion__range=(fecha_inicio, fecha_fin))
        except Exception as e:
            raise ValidationError(f"Error al filtrar por rango de fechas: {str(e)}")

    
class Sensor(ModelBase):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    estado = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    
    objects = SensorManager()
    
    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        unique_together = ['nombre', 'ubicacion']
        
    def activate(self):
        try:
            if not self.active:
                self.active = True
                self.save(update_fields=['active'])
        except Exception as e:
            raise ValidationError(f"No se pudo activar el sensor {self.id}: {str(e)}")
    
    def delete(self, *args, **kwargs):
        try:
            if self.active:
                self.active = False
                self.save(update_fields=['active'])
        except Exception as e:
            raise ValidationError(f"No se pudo desactivar el sensor {self.id}: {str(e)}")
        
    def deactivate(self):
        try:
            if self.active:
                self.active = False
                self.save(update_fields=['active'])
        except Exception as e:
            raise ValidationError(f"No se pudo desactivar el sensor {self.id}: {str(e)}")
        
    def __str__(self):
        return self.nombre

class ReservacionManager(models.Manager):
    def activas(self):
        try:
            return self.filter(active=True)
        except Exception as e:
            raise ValidationError(f"Error al obtener reservaciones activas: {str(e)}")
    
    def mas_reciente(self):
        try:
            return self.filter(active=True).order_by('-fecha_reservacion').first()
        except Exception as e:
            raise ValidationError(f"Error al obtener la reservación más reciente: {str(e)}")
    
    def por_usuario(self, usuario):
        try:
            return self.filter(usuario=usuario).select_related('sensor_activado')
        except Exception as e:
            raise ValidationError(f"Error al filtrar por usuario: {str(e)}")
    
    def mas_reciente_usuario(self, usuario):
        try:
            return self.activas().filter(usuario=usuario).select_related('sensor_activado').order_by('-fecha_reservacion').first()
        except Exception as e:
            raise ValidationError(f"Error al obtener la reservación más reciente por usuario: {str(e)}")

class Reservacion(ModelBase):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_reservacion = models.DateTimeField()
    sensor_activado = models.ForeignKey(Sensor, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    placa = models.CharField(max_length=250)
    objects = ReservacionManager()
    
    class Meta:
        verbose_name = 'Reservacion'
        verbose_name_plural = 'Reservaciones'
        unique_together = ['fecha_reservacion']
    
    def activate(self):
        try:
            if not self.active:
                self.active = True
                self.save(update_fields=['active'])
        except Exception as e:
            raise ValidationError(f"No se pudo activar la reservación {self.id}: {str(e)}")
            
    # def delete(self, *args, **kwargs):
    #     try:
    #         if self.active:
    #             self.active = False
    #             self.save(update_fields=['active'])
    #     except Exception as e:
    #         raise ValidationError(f"No se pudo desactivar la reservación {self.id}: {str(e)}")
    def deactivate_if_sensor_inactive(self):
        try:
            if self.active and self.sensor_activado and not self.sensor_activado.estado:
                self.active = False
                self.save(update_fields=['active'])
        except Exception as e:
            raise ValidationError(f"No se pudo desactivar la reservación {self.id}: {str(e)}")
    def __str__(self):
        return f"Reservacion {self.id} - {self.fecha_reservacion}"

