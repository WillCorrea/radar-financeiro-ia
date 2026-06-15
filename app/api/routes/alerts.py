from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Alert

router = APIRouter(tags=["alerts"])


@router.get("/alerts")
def list_alerts(
    limit: int = Query(10, ge=1, le=100),
    alert_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, List[Dict[str, Any]]]:
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)

    alerts = query.limit(limit).all()
    return {"items": [_serialize_alert(alert) for alert in alerts]}


def _serialize_alert(alert: Alert) -> Dict[str, Any]:
    return {
        "id": alert.id,
        "alert_type": alert.alert_type,
        "title": alert.title,
        "content": alert.content,
        "ticker": alert.asset.ticker if alert.asset else None,
        "created_at": alert.created_at.isoformat(),
    }
