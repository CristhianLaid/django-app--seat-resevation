from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.shortcuts import render
import cv2
from django.views import View
import pytesseract
import re
import threading
from threading import Lock
from apps.reservation.models import Reservacion
from .ardruino_control import ArduinoController
import time

class VideoCameraView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock = Lock()
        self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract'
        self.update_placas_validas()
        self.placas_detectadas_recientemente = []
        self.placa_valida_detectada = None

    def __del__(self):
        self.video.release()

    def get_frame(self):
        with self.lock:
            ret, frame = self.video.read()
            if not ret:
                return None

            gris, canny = self.preprocesar_frame(frame)
            info_placa = self.encontrar_placa(frame, canny)

            if info_placa:
                x, y, w, h, contorno = info_placa
                placa_valida = self.procesar_placa(frame, gris, x, y, w, h, contorno)
                if placa_valida:
                    self.enviar_comando_arduino(placa_valida)
                    self.placa_valida_detectada = placa_valida

            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()

    def preprocesar_frame(self, frame):
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gris = cv2.blur(gris, (3, 3))
        canny = cv2.Canny(gris, 150, 200)
        canny = cv2.dilate(canny, None, iterations=1)
        return gris, canny

    def encontrar_placa(self, frame, canny):
        contornos, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        for c in contornos:
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            epsilon = 0.09 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)
            if len(approx) == 4 and area > 3400:
                relacion_aspecto = float(w) / h
                if 2.1 < relacion_aspecto < 5:
                    return x, y, w, h, c
        return None

    def procesar_placa(self, frame, gris, x, y, w, h, contorno):
        cv2.drawContours(frame, [contorno], 0, (0, 255, 0), 2)
        img_placa = gris[y:y + h, x:x + w]
        texto = pytesseract.image_to_string(img_placa, config='--psm 8')
        texto = texto.strip().replace(" ", "").upper()

        texto_limpio = self.limpiar_placa(texto)

        placa_valida = self.validar_placa(texto_limpio)
        if placa_valida:
            self.placas_validas = list(Reservacion.objects.filter(active=False).values_list('placa', flat=True).distinct())
            print(f"Placa válida detectada: {texto_limpio}")
        else:

            print(f"Placa inválida detectada: {texto_limpio}")

        color = (0, 255, 0) if placa_valida else (0, 0, 255)
        mensaje = "Placa válida" if placa_valida else "Placa inválida"
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        cv2.putText(frame, mensaje, (x - 20, y - 10), 1, 2.2, color, 3)
        return placa_valida

    def limpiar_placa(self, placa):
        return re.sub(r'[-.,_]', '', placa)

    def validar_placa(self, placa):
        return placa in self.placas_validas and placa not in self.placas_detectadas_recientemente

    def update_placas_validas(self):
        self.placas_validas = list(Reservacion.objects.values_list('placa', flat=True).distinct())

    def enviar_comando_arduino(self, placa):
        if placa:
            arduino_controller = ArduinoController()
            if not arduino_controller.luz_verde_encendida:
                arduino_controller.mantener_luz_verde()
                self.placas_detectadas_recientemente.append(placa)
                threading.Thread(target=self.restaurar_estado_arduino, args=(placa,)).start()
                self.apagar_camara()

    def restaurar_estado_arduino(self, placa):
        time.sleep(10)  # Mantener la luz verde encendida durante 10 segundos
        arduino_controller = ArduinoController()
        arduino_controller.actualizar_estado_luces(False)  # Apagar luz verde y encender luz roja
        self.placas_detectadas_recientemente.remove(placa)
        self.reiniciar_camara()  # Reiniciar la cámara

    def reiniciar_camara(self):
        with self.lock:
            self.video.release()
            self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    def apagar_camara(self):
        with self.lock:
            self.video.release()

    def encender_camara(self):
        with self.lock:
            if not self.video.isOpened():
                self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
class VideoFeedView(View):
    def get(self, request):
        camera_view = VideoCameraView()
        return StreamingHttpResponse(self.gen(camera_view), content_type='multipart/x-mixed-replace; boundary=frame')

    def gen(self, camera_view):
        while True:
            frame = camera_view.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                time.sleep(1)
def index(request):
    return render(request, 'reconocimiento/index.html')

class ArduinoView(View):
    def get(self, request):
        thread = threading.Thread(target=self.start_arduino)
        thread.daemon = True
        thread.start()
        return HttpResponse("Arduino control started.")

    def start_arduino(self):
        controller = ArduinoController()
        controller.run()

def obtener_estado_puestos(request):
    controller = ArduinoController()
    estado_puestos = controller.obtener_estado_puestos()
    return JsonResponse(estado_puestos)
