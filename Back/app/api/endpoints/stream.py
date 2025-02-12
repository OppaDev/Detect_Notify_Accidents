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

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await video_service.connect(websocket)
        logger.info(f"Buscando modelo en: {settings.MODEL_PATH}")
        
        # Inicializar YOLO
        try:
            await yolo_service.initialize(settings.MODEL_PATH)
            logger.info("YOLO inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar YOLO: {str(e)}")
            await websocket.close(code=1001, reason="Error al inicializar YOLO")
            return

        # Inicializar la cámara
        logger.info("Intentando inicializar la cámara...")
        if not await try_reconnect_camera(video_service):
            logger.error("No se pudo inicializar la cámara")
            await websocket.close(code=1001, reason="No se pudo inicializar la cámara")
            return
        
        logger.info("Iniciando streaming de video")
        frame_count = 0
        
        while True:
            # Cambiamos la verificación de desconexión
            try:
                # Intentamos hacer un ping para verificar la conexión
                if not websocket.client_state.connected:
                    logger.info("Cliente desconectado, terminando streaming")
                    break

                frame_buffer = await video_service.get_frame()
                if frame_buffer is None:
                    logger.warning("Frame vacío recibido")
                    await asyncio.sleep(0.1)  # Pequeña pausa antes de reintentar
                    continue

                # Convertir el buffer a frame
                frame_array = np.frombuffer(frame_buffer, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                if frame is None:
                    logger.warning("Error al decodificar el frame")
                    continue

                try:
                    # Realizar detección YOLO
                    results = await yolo_service.detect(frame)
                    boxes = yolo_service.get_boxes(results)

                    # Dibujar las detecciones en el frame
                    for box in boxes:
                        bbox = box['bbox']
                        conf = box['conf']
                        cls = box['class']
                        
                        x1, y1, x2, y2 = map(int, bbox)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"C{cls}:{conf:.2f}", (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Convertir frame procesado a JPEG
                    _, processed_buffer = cv2.imencode('.jpg', frame)
                    
                    # Enviar frame
                    await websocket.send_bytes(processed_buffer.tobytes())
                    frame_count += 1
                    if frame_count % 100 == 0:
                        logger.debug(f"Frames procesados: {frame_count}")

                except Exception as e:
                    logger.error(f"Error en el procesamiento YOLO: {str(e)}")
                    # Enviar frame sin procesar en caso de error
                    await websocket.send_bytes(frame_buffer.tobytes())

            except WebSocketDisconnect:
                logger.info("Cliente desconectado durante el streaming")
                break
            except Exception as e:
                logger.error(f"Error en el proceso de streaming: {str(e)}")
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info("Cliente desconectado normalmente")
    except Exception as e:
        logger.error(f"Error general en websocket: {str(e)}")
    finally:
        video_service.disconnect(websocket)
        logger.info(f"Conexión cerrada y recursos liberados. Total frames procesados: {frame_count}")