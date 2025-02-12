from fastapi import FastAPI
from app.core import settings
from app.api.endpoints import stream_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

@app.get("/")
async def root():
    return {"message": "Fall Detection API Running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(stream_router, prefix=settings.API_V1_STR)
