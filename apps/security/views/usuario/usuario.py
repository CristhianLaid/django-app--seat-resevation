from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def CreateUserView(request):
    if request.method == 'POST':
        # Convierte los datos JSON en un diccionario Python
        data = json.loads(request.body)
        
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            is_active=data["isActive"]
        )
        user.save()
        return JsonResponse({'message': 'Usuario creado correctamente'}, status=201)

    # Si la solicitud no es de tipo POST, devuelve un error de método no permitido
    return JsonResponse({'error': 'Método no permitido'}, status=405)

