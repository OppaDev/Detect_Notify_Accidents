from fastapi import FastAPI
from app.core import settings
from app.services.firebase_service import FirebaseService
from app.api.endpoints import stream_router, notifications_router
from app.core.logging_config import setup_logging
from app.services.notification_listener import NotificationListener
import logging
from datetime import datetime

# Configurar logging al inicio
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Iniciando {settings.APP_NAME}")
    logger.info(f"Modo debug: {settings.DEBUG}")
    
    # Verificar configuración de Firebase
    try:
        firebase_service = FirebaseService()
        firebase_service.initialize(
            cred_path=settings.FIREBASE_CRED_PATH,
            database_url=settings.FIREBASE_DATABASE_URL
        )
        logger.info("Firebase inicializado correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar Firebase: {str(e)}")
        raise
    
    # Iniciar listener de notificaciones
    try:
        notification_listener = NotificationListener()
        notification_listener.start_listening()
        logger.info("Servicio de notificaciones iniciado")
    except Exception as e:
        logger.error(f"Error al iniciar servicio de notificaciones: {str(e)}")
        raise
    

@app.get("/")
async def root():
    return {"message": "Fall Detection API Running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-firebase")
async def test_firebase():
    try:
        firebase_service = FirebaseService()
        firebase_service.initialize(
            cred_path=settings.FIREBASE_CRED_PATH,
            database_url=settings.FIREBASE_DATABASE_URL
        )
        test_data = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'message': 'Prueba de conexión'
        }
        await firebase_service.save_detection(test_data)
        return {"status": "success", "message": "Datos guardados en Firebase"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.include_router(
    stream_router,
    prefix=settings.API_V1_STR,
    tags=["stream"]
)

app.include_router(
    notifications_router,
    prefix=settings.API_V1_STR,
    tags=["notifications"]
)