from typing import Dict

from fastapi import FastAPI

from app.api.routes.alerts import router as alerts_router
from app.api.routes.health import router as health_router
from app.api.routes.messages import router as messages_router
from app.api.routes.radar import router as radar_router
from app.config import settings
from database.connection import init_db

app = FastAPI(
    title="Radar Financeiro IA",
    description="Plataforma de monitoramento financeiro inteligente",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(radar_router)
app.include_router(alerts_router)
app.include_router(messages_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Radar Financeiro IA API"}
