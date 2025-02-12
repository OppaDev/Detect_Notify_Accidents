# app/api/endpoints/stream.py
from fastapi import APIRouter, WebSocket
from app.services.video_service import VideoService
from app.core.config import settings

router = APIRouter()
video_service = VideoService()

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    if not await video_service.initialize_camera(settings.CAMERA_URL):
        await websocket.close(code=1000)
        return
    
    try:
        while True:
            frame = await video_service.get_frame()
            if frame is None:
                break
            # Aquí posteriormente añadiremos el procesamiento
            await websocket.send_bytes(frame.tobytes())
    except Exception as e:
        print(f"Error in websocket: {e}")
    finally:
        await websocket.close()
