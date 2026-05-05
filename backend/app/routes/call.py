from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.core.dependencies import get_realtime_call_service
from app.core.websocket_manager import ws_manager

router = APIRouter()


class InitiateCallPayload(BaseModel):
    lead_id: str
    phone_number: str


@router.post("/initiate")
async def initiate_call(payload: InitiateCallPayload, call_service=Depends(get_realtime_call_service)) -> dict:
    result = await call_service.initiate_call(payload.lead_id, payload.phone_number)
    await call_service.ensure_session_runner(result["call_id"])
    return result


@router.websocket("/dashboard")
async def dashboard_events(websocket: WebSocket) -> None:
    await ws_manager.connect("dashboard", websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect("dashboard", websocket)
