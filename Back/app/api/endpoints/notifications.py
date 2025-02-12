# app/api/endpoints/notifications.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.notification_listener import NotificationListener
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
notification_listener = NotificationListener()

@router.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    """Endpoint WebSocket para recibir notificaciones en tiempo real"""
    try:
        await notification_listener.connect(websocket)
        
        while True:
            # Mantener la conexión viva
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        logger.info("Cliente desconectado normalmente")
        notification_listener.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en conexión WebSocket: {str(e)}")
        notification_listener.disconnect(websocket)
