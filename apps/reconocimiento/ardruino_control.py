import serial
import time
import threading

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
        self.sensores_activados = []
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
            if line == "Sensor 1 Activado":
                print("El sensor 1 está activado.")
                if "Sensor 1" not in self.sensores_activados:
                    self.sensores_activados.append("Sensor 1")
            elif line == "Sensor 1 Desactivado":
                print("El sensor 1 está desactivado.")
                if "Sensor 1" in self.sensores_activados:
                    self.sensores_activados.remove("Sensor 1")
            elif line == "Sensor 2 Activado":
                print("El sensor 2 está activado.")
                if "Sensor 2" not in self.sensores_activados:
                    self.sensores_activados.append("Sensor 2")
            elif line == "Sensor 2 Desactivado":
                print("El sensor 2 está desactivado.")
                if "Sensor 2" in self.sensores_activados:
                    self.sensores_activados.remove("Sensor 2")
            print(f"Sensores activados: {self.sensores_activados}")

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
        total_puestos = 2  # Número total de puestos
        puestos_ocupados = len(self.sensores_activados)
        puestos_libres = total_puestos - puestos_ocupados
        return {
            "puestos_ocupados": puestos_ocupados,
            "puestos_libres": puestos_libres
        }
