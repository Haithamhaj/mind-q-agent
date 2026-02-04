import asyncio
import logging
from typing import Dict, List, Any, AsyncGenerator

logger = logging.getLogger(__name__)

class EventBus:
    """
    Simple in-memory Event Bus for broadcasting events to subscribers.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.queues = []
        return cls._instance

    def __init__(self):
        # We use a list of queues. Each subscriber gets their own queue.
        # This is a fan-out pattern.
        if not hasattr(self, 'queues'):
             self.queues: List[asyncio.Queue] = []

    async def subscribe(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribe to events. Returns an async generator that yields events.
        """
        queue = asyncio.Queue()
        self.queues.append(queue)
        try:
            while True:
                # Wait for an event
                event = await queue.get()
                yield event
        except asyncio.CancelledError:
            # Cleanup when subscriber disconnects
            self.queues.remove(queue)
            logger.debug("Subscriber disconnected")

    async def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all subscribers.
        """
        message = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # logger.debug(f"Emitting event: {event_type}")
        
        # Broadcast to all queues
        for queue in self.queues:
            await queue.put(message)

# Global instance
event_bus = EventBus()
