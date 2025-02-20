# app/api/endpoints/stream.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.video_service import VideoService
from app.services.yolo_service import YoloService
from app.core.config import settings
import cv2
import numpy as np
import asyncio
import logging
from app.services.firebase_service import FirebaseService
from datetime import datetime

router = APIRouter()
video_service = VideoService()
yolo_service = YoloService()
logger = logging.getLogger(__name__)

async def try_reconnect_camera(video_service, max_attempts=3):
    """Intenta reconectar la cámara"""
    for attempt in range(max_attempts):
        logger.info(f"Intento de reconexión {attempt + 1}/{max_attempts}")
        if await video_service.initialize_camera(settings.CAMERA_URL):
            logger.info("Reconexión exitosa")
            return True
        await asyncio.sleep(1)
    logger.error("Todos los intentos de reconexión fallaron")
    return False

# Inicializar servicios
firebase_service = FirebaseService()

@router.on_event("startup")
async def startup_event():
    """Inicializar Firebase al inicio"""
    try:
        firebase_service.initialize(
            cred_path=settings.FIREBASE_CRED_PATH,
            database_url=settings.FIREBASE_DATABASE_URL
        )
    except Exception as e:
        logger.error(f"Error al inicializar Firebase: {str(e)}")

# app/api/endpoints/stream.py

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await video_service.connect(websocket)

    try:
        await yolo_service.initialize(settings.MODEL_PATH)
    except Exception as e:
        logger.error(f"Error al inicializar YOLO: {str(e)}")
        await websocket.close(1001)
        video_service.disconnect(websocket)  # Desconectar también en caso de error
        return

    # Inicializar cámara si no está iniciada
    if not video_service.camera_manager.is_running:
        if not await video_service.initialize_camera(settings.CAMERA_URL):
            await websocket.close(1001)
            video_service.disconnect(websocket)  # Desconectar también en caso de error
            return

    try:
        while True:
            frame = await video_service.get_frame()
            if frame:
                try:  # Añade un bloque try...except dentro del bucle
                    await process_frame(frame, websocket)
                except Exception as e:
                    logger.error(f"Error al procesar el frame: {e}")
                    break  # Sale del bucle si hay un error al procesar el frame
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en el websocket principal: {e}")
    finally:
        video_service.disconnect(websocket)  # Asegurar la desconexión aquí también


async def process_frame(frame_buffer, websocket: WebSocket):
    try:
        frame_array = np.frombuffer(frame_buffer, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

        # Detecta y encola la notificacion si se detecta
        await yolo_service.detect_and_notify(frame)
        # Procesa y agrega bordes a las detecciones
        results = await yolo_service.detect(frame)
        boxes = yolo_service.get_boxes(results)

        # Dibujar detecciones de YOLO en el frame
        for box in boxes:
            x1, y1, x2, y2 = map(int, box['bbox'])
            color = (0, 0, 255) if box['class'] == 0 else (0, 255, 0)
            label = "CAIDA" if box['class'] == 0 else "PERSONA"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label}:{box['conf']:.2f}",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Enviar frame procesado al cliente
        _, processed_buffer = cv2.imencode('.jpg', frame)
        await websocket.send_bytes(processed_buffer.tobytes())

    except Exception as e:
        logger.error(f"Error al procesar el frame: {e}")
        raise