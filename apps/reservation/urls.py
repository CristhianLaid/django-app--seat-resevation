from django.urls import path
from apps.reservation.views.sensor import createSensor

urlpatterns = []

urlpatterns+=[
    path('sensor/', createSensor, name='sensor'),
]
