from fastapi import FastAPI

from app.api import health
from app.logging_config import setup_logging
from app.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()

    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
    app.include_router(health.router)
    return app


app = create_app()
