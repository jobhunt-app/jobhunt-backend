from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from app.api import health
from app.logging_config import setup_logging
from app.settings import Settings

settings = Settings()


def create_app() -> FastAPI:

    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(health.router)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_async_engine(settings.database_url)
    app.state.engine = engine  # make it reachable from endpoints
    yield  # ← the app runs here, serving requests
    await engine.dispose()  # shutdown: close all connections


app = create_app()
