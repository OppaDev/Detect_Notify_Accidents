# app/services/firebase_service.py

import firebase_admin
from firebase_admin import credentials, db

class FirebaseService:
    def __init__(self):
        self.app = None
        self.db = None

    def initialize(self, cred_path: str, database_url: str):
        """
        Inicializa la conexión con Firebase
        """
        if not self.app:
            cred = credentials.Certificate(cred_path)
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            self.db = db.reference()

    async def save_detection(self, detection_data: dict):
        """
        Guarda una detección en Firebase
        """
        if not self.db:
            raise Exception("Firebase no ha sido inicializado")
        
        try:
            self.db.child('detections').push(detection_data)
        except Exception as e:
            raise Exception(f"Error al guardar en Firebase: {str(e)}")
