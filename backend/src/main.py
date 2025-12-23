from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import get_settings
from .api.v1 import auth, users, couples, messages, photos, diaries, todos
from .websocket import handler

settings = get_settings()

app = FastAPI(
    title="情侣小空间 API",
    description="A private digital space for couples",
    version="1.0.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(couples.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(photos.router, prefix="/api/v1")
app.include_router(diaries.router, prefix="/api/v1")
app.include_router(todos.router, prefix="/api/v1")

app.include_router(handler.router, prefix="/ws")


@app.on_event("startup")
async def startup_event():
    logger.info("Couple Space API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Couple Space API shutting down...")


@app.get("/")
async def root():
    return {"message": "Welcome to Couple Space API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
