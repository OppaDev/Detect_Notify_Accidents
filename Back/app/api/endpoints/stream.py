# app/api/endpoints/stream.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.video_service import VideoService
from app.core.config import settings

router = APIRouter()
video_service = VideoService()

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await video_service.connect(websocket)
        
        if not await video_service.initialize_camera(settings.CAMERA_URL):
            await websocket.close(code=1001, reason="No se pudo inicializar la cámara")
            return
        
        while True:
            frame = await video_service.get_frame()
            if frame is None:
                break
            await websocket.send_bytes(frame.tobytes())

    except WebSocketDisconnect:
        print("Cliente desconectado normalmente")
    except Exception as e:
        print(f"Error en websocket: {str(e)}")
    finally:
        video_service.disconnect(websocket)
