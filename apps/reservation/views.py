import serial
import time
import threading
import re
from django.core.exceptions import ValidationError
from apps.reservation.models import Sensor

class ArduinoController:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ArduinoController, cls).__new__(cls)
                    cls._instance.__init_serial(*args, **kwargs)
        return cls._instance

    def __init_serial(self, port='COM4', baud_rate=115200, timeout=1):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.sensores = {}  # Diccionario para almacenar el estado de los sensores
        self.luz_verde_encendida = False
        self.ser = None
        self.connect_serial()

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            print("Conectado a Arduino en el puerto", self.port)
        except serial.SerialException as e:
            print(f"Error al conectar con Arduino: {e}")
            self.ser = None

    def enviar_comando(self, comando):
        if self.ser:
            try:
                self.ser.write(comando.encode('utf-8'))
                self.ser.write(b'\n')
                print(f"Comando enviado: {comando}")
            except serial.SerialException as e:
                print(f"Error al enviar comando: {e}")
                self.reconnect_serial()

    def reconnect_serial(self):
        print("Intentando reconectar con Arduino...")
        if self.ser:
            self.ser.close()
        time.sleep(5)
        self.connect_serial()

    def leer_sensores(self):
        if self.ser and self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').rstrip()
            match = re.match(r'Sensor (\d+) (Activado|Desactivado)', line)
            if match is not None:
                sensor_id = match.group(1)
                estado = match.group(2) == 'Activado'
                self.sensores[sensor_id] = estado
                print(f"Sensor {sensor_id} {'activado' if estado else 'desactivado'}.")

                # Actualizar o crear el estado del sensor en la base de datos
                sensor_nombre = f'Sensor {sensor_id}'
                try:
                    sensor, created = Sensor.objects.get_or_create(
                        nombre=sensor_nombre, 
                        defaults={'ubicacion': 'Desconocida', 'estado': estado}
                    )
                    if not created:
                        sensor.estado = estado
                        sensor.save(update_fields=['estado'])
                    if created:
                        print(f"Nuevo sensor creado: {sensor_nombre}")
                    else:
                        print(f"Sensor {sensor_nombre} actualizado")
                except Exception as e:
                    print(f"Error al actualizar o crear el estado del sensor {sensor_id}: {str(e)}")

            else:
                print(f"No se encontró un patrón válido en la línea recibida: {line}")

        else:
            print("No hay datos disponibles para leer desde el puerto serial.")

    def actualizar_estado_luces(self, estado):
        comando = "Encender Verde Independiente" if estado else "Apagar Todas Las Luces"
        self.enviar_comando(comando)
        print(f"Luz {'verde' if estado else 'apagada'} encendida")
        self.luz_verde_encendida = estado

    def mantener_luz_verde(self):
        if not self.luz_verde_encendida:
            self.actualizar_estado_luces(True)
            threading.Timer(10, self.actualizar_estado_luces, [False]).start()

    def run(self):
        try:
            while True:
                self.leer_sensores()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Interrupción de teclado. Cerrando conexión.")
        except serial.SerialException as e:
            print(f"Error de comunicación serial: {e}")
        finally:
            if self.ser:
                self.ser.close()

    def obtener_estado_puestos(self):
        total_puestos = len(self.sensores)  # Número total de puestos basado en la cantidad de sensores
        puestos_ocupados = sum(self.sensores.values())
        puestos_libres = total_puestos - puestos_ocupados
        return {
            "puestos_ocupados": puestos_ocupados,
            "puestos_libres": puestos_libres
        }
