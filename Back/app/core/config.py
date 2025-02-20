# app/core/config.py
from pydantic_settings import BaseSettings
import os
from typing import ClassVar


class Settings(BaseSettings):
    APP_NAME: str = "Fall Detection API"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Configuraciones para video
    CAMERA_URL: str = "http://192.168.0.102:4747/video"
    
    # Configuración del modelo YOLO
    BASE_DIR: ClassVar[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH: str = os.path.join(BASE_DIR, "best.pt")
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"Ruta del modelo configurada: {self.MODEL_PATH}")
        try:
            self.validate_paths()
        except Exception as e:
            print(f"Error en la validación de configuración: {str(e)}")

    def validate_paths(self):
        """Validar rutas y configuraciones críticas"""
        if not os.path.exists(self.MODEL_PATH):
            raise FileNotFoundError(
                f"ERROR CRÍTICO: Modelo no encontrado en {self.MODEL_PATH}"
            )
        return True
    #Configuración de Firebase
    FIREBASE_CRED_PATH: str = "app/core/credentials/firebase-credenciales.json"
    FIREBASE_DATABASE_URL: str = "https://fallapp-6d506-default-rtdb.firebaseio.com"
    
    # Configuración de detección
    DETECTION_THRESHOLD: float = 0.9  # Umbral de confianza para notificaciones
    NOTIFICATION_COOLDOWN: int = 50  # Segundos entre notificaciones


settings = Settings()

