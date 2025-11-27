import asyncio, json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.schemas import SubmitRequest, SubmitResponse, RequestStatusResponse
from db.database import get_db
from db.models import Request, Result
from services.queue import QueueService
from services.status import update_status, get_events

router = APIRouter()

@router.post("/submit", response_model=SubmitResponse)
def submit(body: SubmitRequest, db: Session = Depends(get_db)):
    url = str(body.input_value)
    if "github.com/" not in url:
        raise HTTPException(400, "Only GitHub profile URLs are supported")

    req = Request(input_type="url", input_value=url)
    db.add(req)
    db.commit()
    db.refresh(req)

    update_status(db, req.id, "received", "received", 0.0)
    QueueService.get().enqueue_agent1(req.id)

    return SubmitResponse(request_id=req.id, status=req.status)

@router.get("/request/{request_id}", response_model=RequestStatusResponse)
def get_request(request_id: str, db: Session = Depends(get_db)):
    req = db.get(Request, request_id)
    if not req:
        raise HTTPException(404, "request_id not found")

    res = db.get(Result, request_id)
    return RequestStatusResponse(
        request_id=req.id,
        status=req.status,
        stage=req.stage,
        progress=req.progress,
        created_at=req.created_at.isoformat(),
        results=res.analogs if res else None,
        error_message=req.error_message
    )

@router.get("/request/{request_id}/stream")
async def stream(request_id: str):
    async def gen():
        last_idx = 0
        while True:
            events = get_events(request_id)
            while last_idx < len(events):
                ev = events[last_idx]
                last_idx += 1
                yield f"event: status\ndata: {json.dumps(ev)}\n\n"

            if events and events[-1].get("status") in ("done", "error"):
                yield f"event: done\ndata: {json.dumps({'status': events[-1]['status']})}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")
