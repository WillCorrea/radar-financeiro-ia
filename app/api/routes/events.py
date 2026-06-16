from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from jobs.events_job import EventsJob

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/run")
def run_events(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Dispara o job de eventos (dividendos, JCP, fatos relevantes).

    Retorna `events: 0` e `message: null` quando não há eventos novos.
    """
    try:
        job = EventsJob(db)
        message = job.run()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if message is None:
        return {"status": "ok", "message": None, "events": 0}

    return {
        "status": "ok",
        "message": message,
        "events": _count_events_in_message(message),
    }


def _count_events_in_message(message: str) -> int:
    return sum(1 for line in message.split("\n") if line.startswith("• "))
