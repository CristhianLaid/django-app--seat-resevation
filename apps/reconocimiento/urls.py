# apps/reconocimiento/urls.py
from django.urls import path
from . import views
from .views import ArduinoView

urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.VideoFeedView.as_view(), name='video_feed'),
    path('start-arduino/', ArduinoView.as_view(), name='start_arduino'),
    path('obtener_estado_puestos/', views.obtener_estado_puestos, name='obtener_estado_puestos'),

]


