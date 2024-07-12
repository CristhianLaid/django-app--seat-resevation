import serial
import time
import threading
import re
from django.core.exceptions import ValidationError
from apps.reservation.models import Reservacion, Sensor

class ArduinoController:
    _instance = None
    _lock = threading.Lock()
    _serial_lock = threading.Lock()  # Lock para sincronizar el acceso al puerto serie

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
        with self._serial_lock:
            try:
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
                print("Conectado a Arduino en el puerto", self.port)
            except serial.SerialException as e:
                print(f"Error al conectar con Arduino: {e}")
                self.ser = None

    def enviar_comando(self, comando):
        with self._serial_lock:
            if self.ser:
                try:
                    self.ser.write(comando.encode('utf-8'))
                    self.ser.write(b'\n')
                    print(f"Comando enviado: {comando}")
                except serial.SerialTimeoutException:
                    print("Timeout al enviar comando, intentando reconectar...")
                    self.reconnect_serial()
                except serial.SerialException as e:
                    print(f"Error al enviar comando: {e}")
                    self.reconnect_serial()

    def reconnect_serial(self):
        with self._serial_lock:
            print("Intentando reconectar con Arduino...")
            if self.ser:
                self.ser.close()
            time.sleep(5)
            retry_count = 0
            max_retries = 5
            while retry_count < max_retries:
                try:
                    self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
                    print("Conectado a Arduino en el puerto", self.port)
                    break
                except serial.SerialException as e:
                    print(f"Error al conectar con Arduino: {e}")
                    self.ser = None
                    retry_count += 1
                    time.sleep(5)
            if retry_count == max_retries:
                print("No se pudo reconectar con Arduino después de varios intentos.")

    def leer_sensores(self):
        with self._serial_lock:
            if self.ser and self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').rstrip()
                match = re.match(r'Sensor (\d+) (Activado|Desactivado)', line)
                if match:
                    sensor_id = match.group(1)
                    estado = match.group(2) == 'Activado'
                    self.sensores[sensor_id] = estado
                    print(f"Sensor {sensor_id} {'activado' if estado else 'desactivado'}.")

                    # Actualizar o crear el estado del sensor en la base de datos
                    sensor_nombre = f'Sensor {sensor_id}'
                    try:
                        sensor, created = Sensor.objects.get_or_create(nombre=sensor_nombre, defaults={'ubicacion': 'Desconocida'})
                        sensor.estado = estado
                        sensor.save(update_fields=['estado'])
                        if created:
                            print(f"Nuevo sensor creado: {sensor_nombre}")

                        # Desactivar la reservación asociada si el sensor está inactivo
                        if not estado:  # Si el sensor está desactivado
                            try:
                                reservacion = Reservacion.objects.get(sensor_activado=sensor, active=True)
                                reservacion.deactivate_if_sensor_inactive()
                                print("Reservación eliminada:", reservacion)
                            except Reservacion.DoesNotExist:
                                pass  # No hay reservación activa asociada al sensor

                    except Exception as e:
                        print(f"Error al actualizar o crear el estado del sensor {sensor_id}: {str(e)}")

                    print(f"Sensores activados: {[k for k, v in self.sensores.items() if v]}")

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
            with self._serial_lock:
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

    def reservar_sensor(self, sensor_id):
        comando = f"Reservar Sensor {sensor_id}"
        print(comando)
        self.enviar_comando(comando)
