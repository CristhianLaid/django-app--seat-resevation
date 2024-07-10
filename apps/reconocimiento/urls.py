# apps/reconocimiento/urls.py
from django.urls import path
from . import views
from .views import ArduinoView

urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('start-arduino/', ArduinoView.as_view(), name='start_arduino'),
]