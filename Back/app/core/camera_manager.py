# app/core/camera_manager.py

import asyncio
import cv2
import numpy as np
from typing import Optional, Dict
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class CameraManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.cap = None
        self.is_running = False
        self.frame_buffer = None
        self.last_frame_time = None
        self.clients: Dict = {}
        self.frame_queue = asyncio.Queue(maxsize=2)
        self.processing_task = None
        self._initialized = True
        logger.info("CameraManager inicializado")

    async def start(self, camera_url: str):
        """Inicia la captura de video en un proceso separado"""
        if self.is_running:
            return

        try:
            self.cap = cv2.VideoCapture(camera_url)
            if not self.cap.isOpened():
                raise RuntimeError("No se pudo abrir la cámara")

            self.is_running = True
            self.processing_task = asyncio.create_task(self._process_frames())
            logger.info("Captura de video iniciada")
        except Exception as e:
            logger.error(f"Error al iniciar la cámara: {str(e)}")
            self.is_running = False
            raise
    async def _reconnect_camera(self, camera_url: str, max_attempts: int = 5, initial_delay: float = 1.0):
        """Intenta reconectar la cámara con retraso exponencial"""
        for attempt in range(max_attempts):
            try:
                logger.info(f"Intento de reconexión {attempt + 1}/{max_attempts}")
                self.cap = cv2.VideoCapture(camera_url)
                if self.cap is None or not self.cap.isOpened():
                    raise RuntimeError("No se pudo abrir la cámara en el intento de reconexión")

                self.is_running = True
                logger.info("Reconexión exitosa")
                return True
            except Exception as e:
                logger.error(f"Error al reconectar la cámara (intento {attempt + 1}): {str(e)}")
                delay = initial_delay * (2 ** attempt)  # Retraso exponencial
                logger.info(f"Reintentando en {delay:.2f} segundos...")
                await asyncio.sleep(delay)

        logger.error("Todos los intentos de reconexión fallaron")
        self.is_running = False
        return False

    async def _process_frames(self):
        """Procesa frames en segundo plano con reconexión automática"""
        while self.is_running:
            try:
                success = await self._capture_frame()
                if not success:
                    logger.warning("Error al capturar frame, intentando reconectar...")
                    # Detener el procesamiento actual antes de intentar reconectar
                    self.stop()
                    if not await self._reconnect_camera(camera_url=self.cap.url):  # Pasar la URL de la cámara
                        logger.error("Reconexión fallida, deteniendo el procesamiento")
                        break  # Salir del bucle si la reconexión falla
                    else:
                        logger.info("Reconexión exitosa, reanudando el procesamiento")
                        continue  # Continuar con el procesamiento si la reconexión es exitosa

                # Mantener solo el frame más reciente
                while not self.frame_queue.empty():
                    try:
                        self.frame_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

                await self.frame_queue.put(self.frame_buffer)

            except Exception as e:
                logger.error(f"Error en procesamiento de frames: {str(e)}")
                await asyncio.sleep(0.01)

    async def _capture_frame(self) -> bool:
        """Captura un frame de la cámara de manera asíncrona"""
        if not self.cap or not self.is_running:
            return False

        try:
            # Ejecutar la captura en un thread separado
            loop = asyncio.get_event_loop()
            ret, frame = await loop.run_in_executor(None, self.cap.read)

            if not ret:
                return False

            # Codificar el frame
            _, buffer = cv2.imencode('.jpg', frame)
            self.frame_buffer = buffer.tobytes()
            self.last_frame_time = datetime.now()
            return True

        except Exception as e:
            logger.error(f"Error al capturar frame: {str(e)}")
            return False

    async def get_frame(self) -> Optional[bytes]:
        """Obtiene el último frame disponible"""
        try:
            return await self.frame_queue.get()
        except Exception as e:
            logger.error(f"Error al obtener frame: {str(e)}")
            return None

    def stop(self):
        """Detiene la captura de video"""
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
        if self.cap:
            self.cap.release()
        self.cap = None
        logger.info("Captura de video detenida")

    def __del__(self):
        self.stop()