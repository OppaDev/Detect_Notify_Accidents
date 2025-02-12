# app/api/endpoints/stream.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.video_service import VideoService
from app.services.yolo_service import YoloService
from app.core.config import settings
import cv2
import numpy as np

router = APIRouter()
video_service = VideoService()
yolo_service = YoloService()

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await video_service.connect(websocket)
        
        print(f"Buscando modelo en: {settings.MODEL_PATH}")
        
        # Inicializar YOLO
        try:
            await yolo_service.initialize(settings.MODEL_PATH)
        except Exception as e:
            print(f"Error al inicializar YOLO: {str(e)}")
            await websocket.close(code=1001, reason="Error al inicializar YOLO")
            return
        
        if not await video_service.initialize_camera(settings.CAMERA_URL):
            await websocket.close(code=1001, reason="No se pudo inicializar la cámara")
            return
        
        while True:
            try:
                frame_buffer = await video_service.get_frame()
                if frame_buffer is None:
                    break

                # Convertir el buffer a frame
                frame_array = np.frombuffer(frame_buffer, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

                try:
                    results = await yolo_service.detect(frame)
                    boxes = yolo_service.get_boxes(results)

                    # Dibujar las detecciones en el frame
                    for box in boxes:
                        bbox = box['bbox']
                        conf = box['conf']
                        
                        # Convertir coordenadas float a int
                        x1, y1, x2, y2 = map(int, bbox)
                        
                        # Dibujar rectángulo y confianza
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f"{conf:.2f}", (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Convertir frame procesado a JPEG
                    _, processed_buffer = cv2.imencode('.jpg', frame)
                    
                    # Verificar si la conexión sigue activa antes de enviar
                    if websocket.client_state.CONNECTED:
                        await websocket.send_bytes(processed_buffer.tobytes())
                    else:
                        break

                except Exception as e:
                    print(f"Error en el procesamiento YOLO: {str(e)}")
                    # Verificar si la conexión sigue activa antes de enviar
                    if websocket.client_state.CONNECTED:
                        await websocket.send_bytes(frame_buffer.tobytes())
                    else:
                        break

            except WebSocketDisconnect:
                print("Cliente desconectado")
                break
            except Exception as e:
                print(f"Error en el proceso de streaming: {str(e)}")
                break

    except WebSocketDisconnect:
        print("Cliente desconectado normalmente")
    except Exception as e:
        print(f"Error en websocket: {str(e)}")
    finally:
        # Asegurarse de limpiar recursos
        video_service.disconnect(websocket)
        print("Conexión cerrada y recursos liberados")
