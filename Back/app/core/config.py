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
    MODEL_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "best.pt")  # Ruta a tu modelo entrenado
    
    class Config:
        env_file = ".env"

settings = Settings()
