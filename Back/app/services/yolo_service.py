# app/services/yolo_service.py

from ultralytics import YOLO

class YoloService:
    def __init__(self):
        self.model = None
        self.initialized = False

    async def initialize(self, model_path: str = "yolov8n.pt"):
        """
        Inicializa el modelo YOLO
        """
        if not self.initialized:
            try:
                self.model = YOLO(model_path)
                self.initialized = True
            except Exception as e:
                raise Exception(f"Error al inicializar YOLO: {str(e)}")

    async def detect(self, frame):
        """
        Realiza la detección en un frame
        """
        if not self.initialized:
            raise Exception("YOLO no ha sido inicializado")
        
        try:
            results = self.model(frame, verbose=False)
            return results[0]  # Retorna el primer resultado
        except Exception as e:
            raise Exception(f"Error en la detección: {str(e)}")

    def get_boxes(self, result):
        """
        Obtiene las cajas delimitadoras del resultado
        """
        boxes = []
        for box in result.boxes:
            b = box.xyxy[0].tolist()  # get box coordinates in (top, left, bottom, right) format
            c = box.cls
            boxes.append({
                'bbox': b,
                'class': int(c),
                'conf': float(box.conf)
            })
        return boxes
