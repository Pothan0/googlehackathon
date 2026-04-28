"""
Sports Media Sentinel — Async In-Memory Event Bus
Replaces Kafka for prototype. Supports pub/sub with topic routing.
"""
import asyncio
import json
import time
from collections import defaultdict, deque
from typing import Any, Callable, Coroutine

Subscriber = Callable[[dict], Coroutine[Any, Any, None]]


class EventBus:
    """Async event bus with topic-based pub/sub and event replay."""

    def __init__(self, max_history: int = 500):
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._history: dict[str, deque[dict]] = defaultdict(lambda: deque(maxlen=max_history))
        self._global_subscribers: list[Subscriber] = []
        self._lock = asyncio.Lock()
        self._stats = {"published": 0, "delivered": 0}

    def subscribe(self, topic: str, handler: Subscriber) -> None:
        """Subscribe to a specific topic."""
        self._subscribers[topic].append(handler)

    def subscribe_all(self, handler: Subscriber) -> None:
        """Subscribe to ALL topics (used by WebSocket broadcaster)."""
        self._global_subscribers.append(handler)

    def unsubscribe_all(self, handler: Subscriber) -> None:
        """Remove a global subscriber."""
        if handler in self._global_subscribers:
            self._global_subscribers.remove(handler)

    async def publish(self, topic: str, data: dict) -> None:
        """Publish an event to a topic."""
        event = {
            "topic": topic,
            "timestamp": time.time(),
            "data": data,
        }
        self._history[topic].append(event)
        self._stats["published"] += 1

        tasks = []
        for handler in self._subscribers.get(topic, []):
            tasks.append(self._safe_call(handler, event))
        for handler in self._global_subscribers:
            tasks.append(self._safe_call(handler, event))

        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_call(self, handler: Subscriber, event: dict) -> None:
        """Call handler with error protection."""
        try:
            await handler(event)
            self._stats["delivered"] += 1
        except Exception:
            pass  # Don't let one bad handler break the bus

    def get_history(self, topic: str, limit: int = 50) -> list[dict]:
        """Get recent events for a topic."""
        history = list(self._history.get(topic, []))
        return history[-limit:]

    def get_all_history(self, limit: int = 100) -> list[dict]:
        """Get recent events across all topics, sorted by time."""
        all_events = []
        for events in self._history.values():
            all_events.extend(events)
        all_events.sort(key=lambda e: e["timestamp"])
        return all_events[-limit:]

    @property
    def stats(self) -> dict:
        return {**self._stats, "topics": len(self._history)}


# Singleton
event_bus = EventBus()
