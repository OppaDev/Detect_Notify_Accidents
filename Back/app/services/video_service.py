# app/services/video_service.py
from app.core.camera_manager import CameraManager
from fastapi import WebSocket
import logging

class VideoService:
    def __init__(self):
        self.camera_manager = CameraManager()
        self.connections = set()
        self.logger = logging.getLogger(__name__)

    async def initialize_camera(self, camera_url: str) -> bool:
        try:
            await self.camera_manager.start(camera_url)
            return True
        except Exception as e:
            self.logger.error(f"Error al inicializar cámara: {str(e)}")
            return False

    async def get_frame(self):
        return await self.camera_manager.get_frame()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        self.logger.info("Nuevo cliente WebSocket conectado")

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)
        self.logger.info("Cliente WebSocket desconectado")
        
        if not self.connections:
            self.camera_manager.stop()
