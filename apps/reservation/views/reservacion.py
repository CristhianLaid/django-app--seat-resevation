import uuid
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from apps.security.models import User
from ..models import Reservacion, Sensor
import json

@csrf_exempt
def crear_reservacion(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)

    try:
        data = json.loads(request.body)
        username = data.get('username')
        sensor_id = data.get('sensorId')
        placa = data.get('placa')
        # Validar que el sensorId sea UUID válidos
        try:
            uuid_sensor_id = uuid.UUID(sensor_id)
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': f'Sensor ID {uuid_sensor_id} no válido'
            }, status=404)
        
        user = get_user_or_fail(username)
        sensor = get_sensor_or_fail(uuid_sensor_id)
        
        # Verificar si el sensor ya está reservado
        if sensor_is_reserved(sensor):
            return JsonResponse({
                'status': 'error',
                'message': f'El sensor con ID {sensor_id} ya está reservado'
            }, status=400)

        reservacion = create_reservacion(user, sensor, placa)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Reservación creada con éxito',
            'reservacion_id': reservacion.id,
        })

    except Http404 as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al crear la reservación: {str(e)}'
        }, status=500)


def create_reservacion(user, sensor, placa):
    reservacion = Reservacion.objects.create(
        usuario=user,
        fecha_reservacion=timezone.now(),
        sensor_activado=sensor,
        placa=placa,
        active=True
    )
    reservacion.save()
    return reservacion

@csrf_exempt
def actualizar_reservacion(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)

    try:
        data = json.loads(request.body)
        sensor_id = data.get('sensorId')
        # Validar que el sensorId sea UUID válido
        try:
            uuid_sensor_id = uuid.UUID(sensor_id)
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': f'Sensor ID {sensor_id} no válido'
            }, status=400)
        
        sensor = get_sensor_or_fail(uuid_sensor_id)

        # Obtener la reservación activa para el sensor
        reservacion = Reservacion.objects.filter(sensor_activado=sensor, active=True).first()

        if not reservacion:
            return JsonResponse({
                'status': 'error',
                'message': f'No hay reservación activa para el sensor con ID {sensor_id}'
            }, status=404)

        # Desactivar la reservación
        reservacion.active = False
        reservacion.save(update_fields=['active'])

        return JsonResponse({
            'status': 'success',
            'message': 'Reservación actualizada con éxito'
        })

    except Http404 as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error al actualizar la reservación: {str(e)}'
        }, status=500)


def get_user_or_fail(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        raise Http404(f"Usuario con el username {username} no se encontrado")

def get_sensor_or_fail(sensor_id):
    try:
        sensor = Sensor.objects.get(id=sensor_id)
        return sensor
    except Sensor.DoesNotExist:
        raise Http404(f"Sensor con id {sensor_id} no encontrado")
    
    
def sensor_is_reserved(sensor):
    return Reservacion.objects.filter(sensor_activado=sensor, active=True).exists()