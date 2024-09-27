import asyncio, contextvars


class Server:
    users: contextvars.ContextVar = contextvars.ContextVar('users')

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port

    async def start_server(self) -> None:
        server = await asyncio.start_server(client_connected_cb=self._client_connected, host=self.host, port=self.port)
        await server.serve_forever()

    def _client_connected(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self.users.set(writer.get_extra_info(name='peername'))
        asyncio.create_task(coro=self.listen_for_messages(reader=reader))

    async def listen_for_messages(self, reader: asyncio.StreamReader) -> None:
        while data := await reader.readline(): print(f'{self.users.get()} -> {data}')


async def main() -> None:
    await Server(host='127.0.0.1', port=8000).start_server()


if __name__ == '__main__':
    asyncio.run(main=main())