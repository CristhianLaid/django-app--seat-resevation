from django.contrib import admin
from apps.reservation.models import Reservacion, Sensor

# Register your models here.
admin.site.register(Reservacion)
admin.site.register(Sensor)
