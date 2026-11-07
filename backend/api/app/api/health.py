from fastapi import APIRouter
from pydantic import BaseModel

from app.settings import Settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=Settings().version)
