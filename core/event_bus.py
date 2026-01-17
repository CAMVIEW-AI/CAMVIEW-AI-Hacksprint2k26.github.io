from typing import Callable, List, Dict
from core.events import Event
import threading
import logging

class EventBus:
    """
    Simple synchronous/asynchronous Event Bus.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Subscribe a handler to a specific event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
    
    def subscribe_all(self, handler: Callable[[Event], None]):
        """Subscribe a handler to ALL events (wildcard)."""
        self.subscribe("*", handler)

    def publish(self, event: Event):
        """Publish an event to all subscribers."""
        # direct match
        handlers = self._subscribers.get(event.event_type, [])
        # wildcard match
        handlers.extend(self._subscribers.get("*", []))

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logging.error(f"Error in event handler {handler.__name__}: {e}")

# Global instance
bus = EventBus()
