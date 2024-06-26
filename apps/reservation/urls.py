from django.urls import path
from apps.reservation.views.reservacion import crear_reservacion, actualizar_reservacion
from apps.reservation.views.sensor import createSensor, detail_one_sensors,updateSensor, deleteSensor, detail_sensor

urlpatterns = []


#Sensores
urlpatterns += [
    path('sensor/save/', createSensor, name='createSensor'),  # Endpoint para crear un sensor
    path('sensor/list/', detail_sensor, name='detailSensor'), # Endpoint para listar todos los sensores
    path('sensor/update/<uuid:idSensor>/', updateSensor, name='updateSensor'),  # Endpoint para actualizar un sensor
    path('sensor/list/<uuid:idSensor>/', detail_one_sensors, name='detailOneSensor'),  # Endpoint para obtener detalles de un sensor
    path('sensor/delete/<uuid:idSensor>/', deleteSensor, name='deleteSensor'), # Endpoint para eliminar un sensor
]

#Servicios
urlpatterns += [
    path('reservacion/save/', crear_reservacion, name='crear_reservacion'), # Endpoint para crear un reservacion
    path('reservacion/update/', actualizar_reservacion, name='actualizar_reservacion'), #Endpoint para actualizar una reservacion
]