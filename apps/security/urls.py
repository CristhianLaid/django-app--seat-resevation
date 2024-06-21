from django.urls import path
from apps.security.views.usuario import usuario

urlpatterns = []

urlpatterns += [
    path('crear_usuario/', usuario.CreateUserView, name='crear_usuario')
]
