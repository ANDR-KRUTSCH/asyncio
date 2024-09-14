import asyncio
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from starlette.applications import Starlette
from starlette.routing import WebSocketRoute
from typing import Coroutine, Any


class UserCounter(WebSocketEndpoint):
    encoding = 'text'
    sockets: list[WebSocket] = list()

    async def on_connect(self, websocket: WebSocket) -> Coroutine[Any, Any, None]:
        await websocket.accept()
        UserCounter.sockets.append(websocket)
        await self._send_count()

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        UserCounter.sockets.remove(websocket)
        await self._send_count()

    async def on_receive(self, websocket: WebSocket, data: Any) -> None: pass

    async def _send_count(self) -> None:
        if len(UserCounter.sockets) > 0:
            task_to_socket = {asyncio.create_task(coro=websocket.send_text(data=str(len(UserCounter.sockets)))): websocket for websocket in UserCounter.sockets}
            done, _ = await asyncio.wait(fs=task_to_socket)
            for task in done:
                if task.exception() is not None:
                    if task_to_socket[task] in UserCounter.sockets: UserCounter.sockets.remove(task_to_socket[task])


app = Starlette(routes=[WebSocketRoute(path='/counter', endpoint=UserCounter)])