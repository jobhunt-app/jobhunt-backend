from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import text

from app.settings import Settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


@router.get("/health")
async def health(request: Request) -> HealthResponse:
    engine = request.app.state.engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            database = "ok"
    except Exception:
        database = "unreachable"

    return HealthResponse(status="ok", version=Settings().version, database=database)
