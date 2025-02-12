# app/api/endpoints/stream.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.video_service import VideoService
from app.services.yolo_service import YoloService
from app.core.config import settings
import cv2
import numpy as np
import asyncio
import logging

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

# app/api/endpoints/stream.py
@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await video_service.connect(websocket)
        
        # Inicializar YOLO
        try:
            await yolo_service.initialize(settings.MODEL_PATH)
        except Exception as e:
            logger.error(f"Error al inicializar YOLO: {str(e)}")
            await websocket.close(1001)
            return

        # Inicializar cámara si no está iniciada
        if not video_service.camera_manager.is_running:
            if not await video_service.initialize_camera(settings.CAMERA_URL):
                await websocket.close(1001)
                return

        while True:
            try:
                frame_buffer = await video_service.get_frame()
                if not frame_buffer:
                    continue

                # Procesar frame con YOLO
                frame_array = np.frombuffer(frame_buffer, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
                results = await yolo_service.detect(frame)
                boxes = yolo_service.get_boxes(results)

                # Dibujar detecciones
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box['bbox'])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"C{box['class']}:{box['conf']:.2f}",
                              (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                _, processed_buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(processed_buffer.tobytes())

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error en streaming: {str(e)}")
                await asyncio.sleep(0.1)

    except Exception as e:
        logger.error(f"Error en websocket: {str(e)}")
    finally:
        video_service.disconnect(websocket)
