import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[channel].add(websocket)

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(channel, set())
            sockets.discard(websocket)
            if not sockets and channel in self._connections:
                del self._connections[channel]

    async def emit(self, channel: str, event: str, payload: dict[str, Any]) -> None:
        message = {"event": event, "payload": payload}
        stale: list[WebSocket] = []
        for socket in list(self._connections.get(channel, set())):
            try:
                await socket.send_json(message)
            except Exception:
                stale.append(socket)

        if stale:
            async with self._lock:
                sockets = self._connections.get(channel, set())
                for socket in stale:
                    sockets.discard(socket)
                if not sockets and channel in self._connections:
                    del self._connections[channel]


ws_manager = WebSocketManager()
