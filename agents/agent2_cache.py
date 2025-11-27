import logging
from sqlalchemy.orm import Session

from core.config import settings
from db.database import SessionLocal
from db.models import ParsedPrompt, Result, SitesCache
from services.status import update_status
from services.queue import QueueService

log = logging.getLogger("agent2")

async def agent2_run(request_id: str):
    db: Session = SessionLocal()
    try:
        parsed = db.get(ParsedPrompt, request_id)
        if not parsed:
            return
        jp = parsed.json_prompt
        fps = set(jp.get("fingerprints", []))

        update_status(db, request_id, "cache_check", "agent2", 0.35)

        for row in db.query(SitesCache).all():
            cached_fps = set(row.normalized_json_prompt.get("fingerprints", []))
            if fps and fps == cached_fps:
                update_status(db, request_id, "cache_hit", "agent2", 0.5)
                db.merge(Result(request_id=request_id, analogs=row.analogs))
                db.commit()
                update_status(db, request_id, "done", "done", 1.0)
                return

        QueueService.get().enqueue_agent3(request_id)

    except Exception as e:
        log.exception("agent2 error: %s", e)
        update_status(db, request_id, "error", "agent2", 1.0, error_message=str(e))
    finally:
        db.close()
