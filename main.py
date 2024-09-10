import asyncio, logging
from asyncio import StreamReader, StreamWriter


class ServerState:

    def __init__(self) -> None:
        self._writers: list[StreamWriter] = list()

    async def add_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._writers.append(writer)
        await self._on_connect(writer=writer)
        asyncio.create_task(coro=self._echo(reader=reader, writer=writer))

    async def _on_connect(self, writer: StreamWriter) -> None:
        writer.write(data=f'Welcome! Current clients numbers: {len(self._writers)}.\n'.encode()); await writer.drain()
        await self._notify_all(message='The new client has been connected.\n')

    async def _echo(self, reader: StreamReader, writer: StreamWriter) -> None:
        try:
            while (data := await reader.readline()) != b'':
                writer.write(data=data); await writer.drain()
            self._writers.remove(writer)
            await self._notify_all(message=f'The client has been disconnected. Current clients number: {len(self._writers)}')
        except BaseException as error:
            logging.exception(msg='Error reading the data from the client.', exc_info=error)
            self._writers.remove(writer)

    async def _notify_all(self, message: str) -> None:
        for writer in self._writers:
            try:
                writer.write(data=message.encode()); await writer.drain()
            except ConnectionError as error:
                logging.exception(msg='Error writing the data to the client.', exc_info=error)
                self._writers.remove(writer)


async def main() -> None:
    server_state = ServerState()

    async def client_connected(reader: StreamReader, writer: StreamWriter) -> None:
        await server_state.add_client(reader=reader, writer=writer)

    server = await asyncio.start_server(client_connected_cb=client_connected, host='127.0.0.1', port=8000)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main=main())