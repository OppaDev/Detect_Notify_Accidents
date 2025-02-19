# app/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, db
import asyncio
from datetime import datetime
import logging
from typing import Dict, Any

class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.app = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        self._initialized = True
        self.last_notification_time = None
        self.notification_cooldown = 30  # segundos entre notificaciones

    def initialize(self, cred_path: str, database_url: str):
        """Inicializa la conexión con Firebase"""
        if not self.app:
            try:
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                self.db = db.reference()
                self.logger.info("Firebase inicializado correctamente")
            except Exception as e:
                self.logger.error(f"Error al inicializar Firebase: {str(e)}")
                raise

    async def save_detection(self, detection_data: Dict[str, Any]) -> bool:
        """
        Guarda una detección en Firebase y envía notificación si es necesario
        """
        if not self.db:
            raise Exception("Firebase no ha sido inicializado")

        try:
            current_time = datetime.now()
            
            # Verificar cooldown de notificaciones
            if (self.last_notification_time and 
                (current_time - self.last_notification_time).total_seconds() < self.notification_cooldown):
                return False

            detection_data.update({
                'timestamp': current_time.isoformat(),
                'status': 'pending'  # pending, processed, ignored
            })

            # Guardar en Firebase
            ref = self.db.child('detections').push(detection_data)
            self.last_notification_time = current_time
            
            # Enviar notificación
            await self._send_notification(detection_data)
            
            self.logger.info(f"Detección guardada con ID: {ref.key}")
            return True

        except Exception as e:
            self.logger.error(f"Error al guardar en Firebase: {str(e)}")
            return False

    async def _send_notification(self, detection_data: Dict[str, Any]):
        """
        Envía notificación a través de Firebase
        """
        try:
            notification_data = {
                'title': 'CAIDA DETECTADA',
                'body': f"Se ha detectado un posible accidente con confianza: {detection_data.get('confidence', 0):.2f}",
                'timestamp': detection_data['timestamp'],
                'status': 'new'
            }
            
            self.db.child('notifications').push(notification_data)
            self.logger.info("Notificación enviada correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al enviar notificación: {str(e)}")
