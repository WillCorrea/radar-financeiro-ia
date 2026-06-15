from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from jobs.daily_radar_job import DailyRadarJob

router = APIRouter(prefix="/radar", tags=["radar"])


@router.post("/run")
def run_radar(db: Session = Depends(get_db)) -> Dict[str, str]:
    try:
        job = DailyRadarJob(db)
        message = job.run()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"status": "ok", "message": message}
