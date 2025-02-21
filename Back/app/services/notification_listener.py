# app/services/notification_listener.py

from firebase_admin import db
import asyncio
from typing import Callable, Dict, List
import logging
from datetime import datetime
from fastapi import WebSocket

class NotificationListener:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationListener, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.active_connections: List[WebSocket] = []
        self.stream = None
        self._initialized = True
        self.loop = None

    async def connect(self, websocket: WebSocket):
        """Conecta un nuevo cliente WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"Nuevo cliente conectado. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Desconecta un cliente WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"Cliente desconectado. Total: {len(self.active_connections)}")

    def start_listening(self):
        """Inicia la escucha de nuevas notificaciones"""
        try:
            self.loop = asyncio.get_event_loop()
            notifications_ref = db.reference('notifications')

            def on_notification(event):
                if event.event_type == 'put' and event.data:
                    notification_data = {
                        'id': event.path[1:],  # Elimina el '/' inicial
                        'data': event.data,
                        'timestamp': datetime.now().isoformat()
                    }
                    self.loop.call_soon_threadsafe(
                        lambda: self.loop.create_task(
                            self._broadcast_notification(notification_data)
                        )
                    )


            self.stream = notifications_ref.listen(on_notification)
            self.logger.info("Listener de notificaciones iniciado")

        except Exception as e:
            self.logger.error(f"Error al iniciar listener: {str(e)}")
            raise

    async def _broadcast_notification(self, notification: Dict):
        """Envía la notificación a todos los clientes conectados"""
        disconnected_clients = []

        for websocket in self.active_connections:
            try:
                await websocket.send_json(notification)
                self.logger.debug(f"Notificación enviada: {notification}")
            except Exception as e:
                self.logger.error(f"Error al enviar notificación: {str(e)}")
                disconnected_clients.append(websocket)

        # Limpia las conexiones cerradas
        for websocket in disconnected_clients:
            self.disconnect(websocket)

    def stop_listening(self):
        """Detiene el listener de notificaciones"""
        if self.stream:
            self.stream.close()
            self.logger.info("Listener de notificaciones detenido")