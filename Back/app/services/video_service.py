# app/services/video_service.py
import cv2
import numpy as np
from typing import Optional
import asyncio

class VideoService:
    def __init__(self):
        self.connections = set()
        self.cap = None
        self.is_running = False

    async def initialize_camera(self, camera_url: str) -> bool:
        """
        Inicializa la conexión con la cámara
        """
        try:
            self.cap = cv2.VideoCapture(camera_url)
            if not self.cap.isOpened():
                print(f"No se pudo abrir la cámara: {camera_url}")
                return False
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error al inicializar la cámara: {str(e)}")
            return False

    async def get_frame(self) -> Optional[np.ndarray]:
        """
        Obtiene un frame de la cámara
        """
        if not self.cap or not self.is_running:
            return None

        try:
            # Simular una operación asíncrona para no bloquear
            await asyncio.sleep(0.01)
            
            ret, frame = self.cap.read()
            if not ret:
                return None

            # Codificar el frame en formato JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer

        except Exception as e:
            print(f"Error al obtener frame: {str(e)}")
            return None

    async def connect(self, websocket):
        """
        Conecta un nuevo cliente WebSocket
        """
        self.connections.add(websocket)
        try:
            await websocket.accept()
        except Exception as e:
            self.connections.remove(websocket)
            raise e

    def disconnect(self, websocket):
        """
        Desconecta un cliente WebSocket
        """
        try:
            self.connections.remove(websocket)
        except KeyError:
            pass  # Si ya fue removido, ignorar
    
        if len(self.connections) == 0:
            self.release_camera()

    def release_camera(self):
        """
        Libera los recursos de la cámara
        """
        if self.cap:
            self.is_running = False
            self.cap.release()
            self.cap = None

    async def broadcast(self, message):
        """
        Envía un mensaje a todos los clientes conectados
        """
        disconnected = set()
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        # Eliminar conexiones cerradas
        for connection in disconnected:
            self.connections.remove(connection)

    def __del__(self):
        """
        Destructor para liberar recursos
        """
        self.release_camera()
