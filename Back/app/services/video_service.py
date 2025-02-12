# app/services/video_service.py
import cv2
from fastapi import WebSocket

class VideoService:
    def __init__(self):
        self.camera = None
    
    async def initialize_camera(self, camera_url: str):
        try:
            self.camera = cv2.VideoCapture(camera_url)
            return self.camera.isOpened()
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    async def get_frame(self):
        if self.camera is None:
            return None
        
        success, frame = self.camera.read()
        if not success:
            return None
        
        return frame
