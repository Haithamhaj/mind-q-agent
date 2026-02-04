from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from mind_q_agent.events.bus import event_bus

router = APIRouter(
    prefix="/ws",
    tags=["realtime"]
)

logger = logging.getLogger(__name__)

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Subscribe to event bus and stream to websocket
        async for event in event_bus.subscribe():
            await websocket.send_json(event)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
