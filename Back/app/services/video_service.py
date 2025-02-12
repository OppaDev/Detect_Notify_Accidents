# app/services/video_service.py
import cv2
import numpy as np
from typing import Optional
import asyncio
import logging
import time

class VideoService:
    def __init__(self):
        self.connections = set()
        self.cap = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        self.reconnect_attempts = 3
        self.reconnect_delay = 2  # segundos

    async def initialize_camera(self, camera_url: str) -> bool:
        """
        Inicializa la conexión con la cámara con reintentos
        """
        for attempt in range(self.reconnect_attempts):
            self.logger.info(f"Intento {attempt + 1}/{self.reconnect_attempts} de conectar a la cámara: {camera_url}")
            try:
                if self.cap is not None:
                    self.cap.release()
                
                self.cap = cv2.VideoCapture(camera_url)
                if not self.cap.isOpened():
                    self.logger.warning(f"No se pudo abrir la cámara en el intento {attempt + 1}")
                    await asyncio.sleep(self.reconnect_delay)
                    continue

                # Verificar si podemos leer un frame
                ret, _ = self.cap.read()
                if not ret:
                    self.logger.warning(f"No se pudo leer frame en el intento {attempt + 1}")
                    await asyncio.sleep(self.reconnect_delay)
                    continue

                self.is_running = True
                self.logger.info("Cámara inicializada exitosamente")
                return True

            except Exception as e:
                self.logger.error(f"Error al inicializar la cámara (intento {attempt + 1}): {str(e)}")
                await asyncio.sleep(self.reconnect_delay)

        self.logger.error("No se pudo inicializar la cámara después de varios intentos")
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
                self.logger.warning("No se pudo leer el frame")
                self.is_running = False
                return None

            # Codificar el frame en formato JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer

        except Exception as e:
            self.logger.error(f"Error al obtener frame: {str(e)}")
            self.is_running = False
            return None

    async def connect(self, websocket):
        """
        Conecta un nuevo cliente WebSocket
        """
        self.logger.info("Nuevo cliente WebSocket conectándose")
        self.connections.add(websocket)
        try:
            await websocket.accept()
            self.logger.info("Cliente WebSocket conectado exitosamente")
        except Exception as e:
            self.logger.error(f"Error al aceptar conexión WebSocket: {str(e)}")
            self.connections.remove(websocket)
            raise e

    def disconnect(self, websocket):
        """
        Desconecta un cliente WebSocket
        """
        try:
            self.connections.remove(websocket)
            self.logger.info("Cliente WebSocket desconectado")
        except KeyError:
            self.logger.warning("Intento de desconectar un cliente que ya no está conectado")
        
        if len(self.connections) == 0:
            self.logger.info("No hay más clientes conectados, liberando recursos de la cámara")
            self.release_camera()

    def release_camera(self):
        """
        Libera los recursos de la cámara
        """
        if self.cap:
            self.is_running = False
            self.cap.release()
            self.cap = None
            self.logger.info("Recursos de la cámara liberados")

    def __del__(self):
        """
        Destructor para liberar recursos
        """
        self.release_camera()
