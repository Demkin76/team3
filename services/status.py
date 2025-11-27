import time
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from db.models import Request

_EVENTS: Dict[str, List[Dict[str, Any]]] = {}

def push_event(request_id: str, payload: Dict[str, Any]):
    _EVENTS.setdefault(request_id, []).append(payload)

def get_events(request_id: str):
    return _EVENTS.get(request_id, [])

def update_status(db: Session, request_id: str, status: str, stage: str, progress: float, error_message: str | None = None):
    req = db.get(Request, request_id)
    if not req:
        return
    req.status = status
    req.stage = stage
    req.progress = progress
    req.error_message = error_message
    db.add(req)
    db.commit()

    push_event(request_id, {
        "status": status,
        "stage": stage,
        "progress": progress,
        "ts": time.time(),
        "error_message": error_message
    })
