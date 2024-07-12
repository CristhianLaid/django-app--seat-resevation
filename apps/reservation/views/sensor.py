from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

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

@csrf_exempt
def detail_one_sensors(request, idSensor):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        sensor = get_object_or_404(Sensor, pk=idSensor)
        return JsonResponse({
            'id': str(sensor.id),
            'nombre': sensor.nombre,
            'ubicacion': sensor.ubicacion,
            'estado': sensor.estado
        })
    
    except Sensor.DoesNotExist:
        return JsonResponse({'error': 'Sensor no encontrado'}, status=404)

@csrf_exempt
def detail_sensor(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        sensors = Sensor.objects.all()
        
        sensors_list = []
        
        for sensor in sensors:
            sensors_list.append({
            'id': str(sensor.id),
            'nombre': sensor.nombre,
            'ubicacion': sensor.ubicacion,
            'estado': sensor.estado
        })
     
        return JsonResponse(sensors_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

""" @csrf_exempt
def updateSensor(request, idSensor):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sensor = get_object_or_404(Sensor, pk=idSensor)
            
            nombre_sensor = data.get('nombre', sensor.nombre)
            ubicacion_sensor = data.get('ubicacion', sensor.ubicacion)
            estado_sensor = data.get('estado', sensor.estado)
            
            # Validar el campo 'estado'
            if estado_sensor not in [True, False, 'true', 'false', 'True', 'False']:
                return JsonResponse({'error': 'Invalid value for estado. Use True or False.'}, status=400)
            
            # Actualizar el sensor con los datos recibidos
            sensor.nombre = nombre_sensor
            sensor.ubicacion = ubicacion_sensor
            sensor.estado = estado_sensor
            
            # Verificar si hay campos para actualizar
            fields_to_update = ['nombre', 'ubicacion', 'estado']
            if any(field in data for field in fields_to_update):
                sensor.save()
                return JsonResponse({'success': 'Sensor updated successfully'})
            
            # Verificar campos faltantes
            required_fields = ['nombre', 'ubicacion']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({'error': f'Missing required fields: {", ".join(missing_fields)}'}, status=400)
            
            return JsonResponse({'error': 'No fields to update'}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        
        except KeyError as e:
            return JsonResponse({'error': f'Missing key in JSON: {str(e)}'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method Not Allowed'}, status=405)
 """
""" @csrf_exempt
def updateSensor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre_sensor = data.get('nombre_sensor')  # Asegúrate de manejar el caso en que 'nombre_sensor' no esté presente

            # Obtener el sensor por su nombre
            sensor = Sensor.objects.get(nombre=nombre_sensor)

            # Cambiar el estado del sensor
            sensor.estado = not sensor.estado  # Cambia el estado al contrario del estado actual

            # Guardar el sensor actualizado en la base de datos
            sensor.save()

            # Devolver una respuesta si es necesario
            return JsonResponse({'message': f'Estado del sensor {nombre_sensor} actualizado correctamente a {sensor.estado}'}, status=200)

        except Sensor.DoesNotExist:
            return JsonResponse({'error': f'No se encontró el sensor con nombre {nombre_sensor}'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405) """
@csrf_exempt
def updateSensor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(request)
            nombre_sensor = data.get('nombre_sensor')  # Asegúrate de manejar el caso en que 'nombre_sensor' no esté presente

            # Obtener el sensor por su nombre
            sensor = Sensor.objects.get(nombre=nombre_sensor)

            # Cambiar el estado del sensor
            sensor.estado = not sensor.estado  # Cambia el estado al contrario del estado actual

            # Guardar el sensor actualizado en la base de datos
            sensor.save()

            # Devolver una respuesta si es necesario
            return JsonResponse({'message': f'Estado del sensor {nombre_sensor} actualizado correctamente a {sensor.estado}'}, status=200)

        except Sensor.DoesNotExist:
            return JsonResponse({'error': f'No se encontró el sensor con nombre {nombre_sensor}'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def deleteSensor(request, idSensor):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        sensor = get_object_or_404(Sensor, pk=idSensor)
        sensor.delete()
        return JsonResponse({'message': 'Sensor deleted successfully'}, status=200)

    except Sensor.DoesNotExist:
        return JsonResponse({'error': 'Sensor not found'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    except KeyError as e:
        return JsonResponse({'error': f'Missing key in JSON: {str(e)}'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
    