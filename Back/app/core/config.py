# app/core/config.py
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    APP_NAME: str = "Fall Detection API"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Configuraciones para video
    CAMERA_URL: str = "http://192.168.100.169:4747/video"
    
    # Configuración del modelo YOLO
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH: str = os.path.join(BASE_DIR, "best.pt")
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"Ruta del modelo configurada: {self.MODEL_PATH}")
        if not os.path.exists(self.MODEL_PATH):
            print(f"ADVERTENCIA: El archivo del modelo no existe en: {self.MODEL_PATH}")

settings = Settings()
