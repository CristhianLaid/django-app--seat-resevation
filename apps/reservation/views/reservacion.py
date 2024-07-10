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
                'message': f'Sensor ID {sensor_id} no válido'
            }, status=400)
        
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
    try:
        reservacion = Reservacion.objects.create(
            usuario=user,
            fecha_reservacion=timezone.now(),
            sensor_activado=sensor,
            placa=placa,
            active=True
        )
        
        sensor.estado = True  # Activar el estado del sensor
        sensor.save(update_fields=['estado'])
        
        return reservacion
    
    except Exception as e:
        raise e

@csrf_exempt
def all_reservations(request):
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)
    
    reservations = Reservacion.objects.all().select_related('usuario', 'sensor_activado')
    
    reservations_list = []
    
    for reservation in reservations:
        sensor_activado = {
                'id': reservation.sensor_activado.id,
                'nombre': reservation.sensor_activado.nombre,
                'ubicacion': reservation.sensor_activado.ubicacion,
                'estado': reservation.sensor_activado.estado,
                'active': reservation.sensor_activado.active,
                'createdAt': reservation.sensor_activado.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updatedAt': reservation.sensor_activado.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            } if reservation.sensor_activado else None
        reservations_list.append({
            'idReservacion': reservation.id,
            "usuario": reservation.usuario.username,
            "fecha_reservacion": reservation.fecha_reservacion.strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_activado": sensor_activado,
            'placa': reservation.placa,
            'activo': reservation.active
        })
    
    return JsonResponse(reservations_list, safe=False)

@csrf_exempt
def get_one_by_id(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)
    
    try:
        data_reservacion = json.loads(request.body)
        print(data_reservacion)
        reservacion_id = data_reservacion.get('reservacionId')

        reservation = get_reservation_or_fail(reservacion_id)
    
        data = {
            'idReservacion': reservation.id,
            "usuario": reservation.usuario.username,
            "fecha_reservacion": reservation.fecha_reservacion.strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_activado": reservation.sensor_activado.nombre,
            'placa': reservation.placa,
            'precio': 10,
            'activo': reservation.active
        } 
        
        return JsonResponse(data, safe=True)
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
    
@csrf_exempt
def getIdReservation(request, reservacion_id):
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)
    
    try:
        reservation = get_reservation_or_fail(reservacion_id)
    
        data = {
            'idReservacion': reservation.id,
            "usuario": reservation.usuario.username,
            "fecha_reservacion": reservation.fecha_reservacion.strftime('%Y-%m-%d %H:%M:%S'),
            "sensor_activado": reservation.sensor_activado.nombre,
            'placa': reservation.placa,
            'activo': reservation.active
        } 
        
        return JsonResponse(data, safe=True)
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
        

@csrf_exempt
def actualizar_reservacion(request):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)

    try:
        data = json.loads(request.body)
        sensor_name = data.get('sensorName')
        
        sensor = Sensor.objects.activos().get(nombre=sensor_name)
        
        # Obtener la reservación activa para el sensor
        reservacion = Reservacion.objects.filter(sensor_activado=sensor, active=True).first()

        if not reservacion:
            return JsonResponse({
                'status': 'error',
                'message': f'No hay reservación activa para el sensor con el nombre {sensor_name}'
            }, status=404)

        # Desactivar la reservación
        reservacion.active = False
        reservacion.save(update_fields=['active'])
        
        sensor.estado = False 
        sensor.save(update_fields=['estado'])

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
    
def get_reservation_or_fail(reservation_id):
    try:
        reservation = get_object_or_404(Reservacion, pk=reservation_id)
        return reservation
    except:
        raise Http404(f"Reservacion con id {reservation_id} no encontrado")

def sensor_is_reserved(sensor):
    return Reservacion.objects.filter(sensor_activado=sensor, active=True).exists()