import asyncio
from asyncio import BaseTransport, Transport, Protocol, Future, AbstractEventLoop


class HTTPGetClientProtocol(Protocol):

    def __init__(self, host: str, event_loop: AbstractEventLoop) -> None:
        self._host: str = host
        self._future: Future = event_loop.create_future()
        self._transport: Transport | None = None
        self._response_buffer: bytes = bytes()

    async def get_response(self) -> str:
        return await self._future
    
    def _get_request_bytes(self) -> bytes:
        return f'GET / HTTP/1.1\r\nConnection: close\r\nHost: {self._host}\r\n\r\n'.encode()
    
    def connection_made(self, transport: BaseTransport) -> None:
        print(f'Connection to <{self._host}> created.')
        self._transport = transport
        self._transport.write(data=self._get_request_bytes())

    def data_received(self, data: bytes) -> None:
        print(f'Data received.')
        self._response_buffer += data

    def eof_received(self) -> bool | None:
        self._future.set_result(self._response_buffer.decode())
        return False
    
    def connection_lost(self, exc: Exception | None) -> None:
        if exc is None: print('Connection was closed clearly.')
        else: self._future.set_exception(exc)


async def make_request(host: str, port: int, event_loop: AbstractEventLoop) -> str:
    def protocol_factory(): return HTTPGetClientProtocol(host=host, event_loop=event_loop)

    _, protocol = await event_loop.create_connection(protocol_factory=protocol_factory, host=host, port=port)

    return await protocol.get_response()

async def main() -> None:
    print(await make_request(host='www.example.com', port=80, event_loop=asyncio.get_running_loop()))


if __name__ == '__main__':
    asyncio.run(main=main())