from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json

from ..models import Sensor

@csrf_exempt
def createSensor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = ['nombre', 'ubicacion']
            
            if not all(field in data for field in required_fields):
                missing_fields = [field for field in required_fields if field not in data]
                return JsonResponse({'error': f'Los campos {", ".join(missing_fields)} son obligatorios'}, status=400)
            
            for field in required_fields:
                if not data[field].strip():
                    return JsonResponse({'error': f'El campo "{field}" no puede estar vacío'}, status=400)
                
            nombreSensor = data.get('nombre', '')
            ubicacionSensor = data.get('ubicacion', '')
            
            if Sensor.objects.filter(nombre=nombreSensor, ubicacion=ubicacionSensor).exists():
                return JsonResponse({'error': f'Ya existe un sensor con nombre "{nombreSensor}" en la ubicación "{ubicacionSensor}"'}, status=400)

            sensor = Sensor.objects.create(nombre=nombreSensor, ubicacion=ubicacionSensor)

            # Devolver los datos del sensor creado en la respuesta JSON
            return JsonResponse({
                'mensaje': 'Sensor creado correctamente',
                'sensor': {
                    'id': sensor.id,
                    'nombre': sensor.nombre,
                    'ubicacion': sensor.ubicacion,
                    'estado': sensor.estado
                }
            }, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return JsonResponse({'error': f'Ya existe un sensor con nombre "{nombreSensor}" en la ubicación "{ubicacionSensor}"'}, status=400)

            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
