from fastapi import APIRouter, Depends, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.dependencies import get_app_settings, get_orchestrator
from app.db.session import get_db
from app.schemas.call import CallCompleteResponse, CallTurnRequest, CallTurnResponse

router = APIRouter()


@router.post("/{call_id}/turns", response_model=CallTurnResponse)
def process_turn(
    call_id: str,
    payload: CallTurnRequest,
    db: Session = Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> CallTurnResponse:
    return orchestrator.process_turn(db, call_id, payload)


@router.post("/{call_id}/complete", response_model=CallCompleteResponse)
def complete_call(
    call_id: str,
    db: Session = Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> CallCompleteResponse:
    return orchestrator.finalize_call(db, call_id)


@router.post("/twilio/voice")
def twilio_voice_webhook(request: Request) -> Response:
    settings = get_app_settings()
    call_id = request.query_params.get("call_id", "")

    ws_base = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")
    stream_url = f"{ws_base}{settings.api_prefix}/calls/stream/{call_id}"

    try:
        from twilio.twiml.voice_response import Connect, VoiceResponse

        response = VoiceResponse()
        response.say("Connecting you to Rupeezy assistant.", voice="alice")
        connect = Connect()
        connect.stream(url=stream_url)
        response.append(connect)
        xml = str(response)
    except ModuleNotFoundError:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<Response><Say>Connecting you to Rupeezy assistant.</Say></Response>"
        )

    return Response(content=xml, media_type="application/xml")


@router.post("/twilio/status", status_code=status.HTTP_204_NO_CONTENT)
async def twilio_status_webhook(
    request: Request,
    db: Session = Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> Response:
    form = await request.form()
    provider_call_id = form.get("CallSid")
    call_status = form.get("CallStatus")
    if provider_call_id and call_status:
        orchestrator.sync_provider_status(db, provider_call_id, call_status)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.websocket("/stream/{call_id}")
async def stream_conversation(call_id: str, websocket: WebSocket) -> None:
    await websocket.accept()
    orchestrator = get_orchestrator()
    db = next(get_db())

    try:
        while True:
            payload = await websocket.receive_json()
            event = payload.get("event", "transcript")

            if event == "transcript":
                turn_request = CallTurnRequest(
                    user_text=payload["user_text"],
                    tone=payload.get("tone"),
                    duration_seconds=payload.get("duration_seconds", 0),
                )
                result = await run_in_threadpool(orchestrator.process_turn, db, call_id, turn_request)
                await websocket.send_json(result.model_dump())
            elif event == "complete":
                result = await run_in_threadpool(orchestrator.finalize_call, db, call_id)
                await websocket.send_json(result.model_dump())
                break
    except WebSocketDisconnect:
        pass
    finally:
        db.close()
