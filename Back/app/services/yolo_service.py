# app/services/yolo_service.py
from ultralytics import YOLO
import os
import logging
from typing import List, Dict

class YoloService:
    def __init__(self):
        self.model = None
        self.initialized = False
        self.logger = logging.getLogger(__name__)

    async def initialize(self, model_path: str = "yolov8n.pt"):
        """Inicializa el modelo YOLO"""
        if not self.initialized:
            try:
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Modelo no encontrado en: {model_path}")
                
                self.logger.info(f"Cargando modelo desde: {model_path}")
                self.model = YOLO(model_path)
                self.initialized = True
                self.logger.info("Modelo YOLO inicializado correctamente")
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
