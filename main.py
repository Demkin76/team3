import asyncio
from fastapi import FastAPI
from api.routes import router as api_router
from core.config import settings
from core.logging import setup_logging
from db.database import init_db
from services.queue import QueueService

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    async def startup():
        await init_db()
        QueueService.get().start_workers()

    @app.on_event("shutdown")
    async def shutdown():
        await QueueService.get().stop_workers()

    return app

app = create_app()
