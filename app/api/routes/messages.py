from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import MessageSent

router = APIRouter(tags=["messages"])


@router.get("/messages")
def list_messages(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Dict[str, List[Dict[str, Any]]]:
    messages = (
        db.query(MessageSent)
        .order_by(MessageSent.sent_at.desc())
        .limit(limit)
        .all()
    )
    return {"items": [_serialize_message(message) for message in messages]}


def _serialize_message(message: MessageSent) -> Dict[str, Any]:
    return {
        "id": message.id,
        "channel": message.channel,
        "content": message.content,
        "user_id": message.user_id,
        "sent_at": message.sent_at.isoformat(),
    }
