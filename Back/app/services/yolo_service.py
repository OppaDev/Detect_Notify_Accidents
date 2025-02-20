# app/services/yolo_service.py
from ultralytics import YOLO
import os
import logging
from typing import List, Dict
from datetime import datetime
from app.core.config import settings
from app.services.firebase_service import FirebaseService  # Importa el servicio Firebase
from typing import List, Dict, Any
class YoloService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YoloService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)
        self.last_notification_time = None
        self.firebase_service = FirebaseService()  # Obtener la instancia de FirebaseService
        self._initialized = True
    async def initialize(self, model_path: str = "best.pt"):
        """Inicializa el modelo YOLO"""
        if not self.initialized:
            try:
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Modelo no encontrado en: {model_path}")

                self.logger.info(f"Cargando modelo desde: {model_path}")
                self.model = YOLO(model_path).to("cuda:0")
                self.initialized = True
                self.logger.info("Modelo YOLO inicializado correctamente con gpu")
            except Exception as e:
                self.logger.error(f"Error al inicializar YOLO: {str(e)}")
                raise Exception(f"Error al inicializar YOLO: {str(e)}")

    async def detect(self, frame):
        """Realiza la detección en un frame"""
        if not self.initialized:
            raise Exception("YOLO no ha sido inicializado")

        try:
            results = self.model(frame, verbose=False)
            return results[0]
        except Exception as e:
            self.logger.error(f"Error en la detección: {str(e)}")
            raise
    async def detect_and_notify(self, frame):
        """
        Realiza la detección y encola una notificación si es necesario
        """
        results = await self.detect(frame)
        boxes = self.get_boxes(results)

        for box in boxes:
            confidence = box['conf']
            class_id = box['class']

            if class_id == 0 and confidence > settings.DETECTION_THRESHOLD and await self.should_send_notification():
                detection_data = {
                    'confidence': float(confidence),
                    'class_id': int(class_id),
                    'bbox': box['bbox'],
                    'location': 'Área de monitoreo 1',
                }
                await self.process_detection(detection_data)

    def get_boxes(self, result) -> List[Dict]:
        """Extrae las cajas delimitadoras de los resultados de YOLO"""
        boxes = []
        try:
            for box in result.boxes:
                # Convertir tensor a lista
                bbox = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                boxes.append({
                    'bbox': bbox,
                    'conf': conf,
                    'class': cls
                })
            return boxes
        except Exception as e:
            self.logger.error(f"Error al procesar boxes: {str(e)}")
            return []
    async def process_detection(self, detection_data: Dict[str, Any]):
        """
        Procesa una detección y encola una tarea para enviar la notificación.
        """
        try:
            # Agrega el timestamp a los datos de la detección
            current_time = datetime.now().isoformat()
            detection_data['timestamp'] = current_time

            # Intenta enviar la notificación usando el servicio Firebase
            success = await self.firebase_service.save_detection(detection_data)

            if success:
                self.update_last_notification_time()
            else:
                self.logger.warning("No se envió la notificación debido al cooldown o un error.")

        except Exception as e:
            self.logger.error(f"Error al encolar la tarea de notificación: {str(e)}")
    async def should_send_notification(self):
        """
        Verifica si se debe enviar una notificación basada en el cooldown
        """
        if not self.last_notification_time:
            return True

        time_since_last = (datetime.now() - self.last_notification_time).total_seconds()
        return time_since_last >= settings.NOTIFICATION_COOLDOWN

    def update_last_notification_time(self):
        """
        Actualiza el tiempo de la última notificación enviada
        """
        self.last_notification_time = datetime.now()