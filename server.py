import asyncio, logging
from asyncio import StreamReader, StreamWriter


class ChatServer:

    def __init__(self) -> None:
        self._username_to_writer: dict[str, StreamWriter] = dict()

    async def start_chat_server(self, host: str, port: int) -> None:
        server = await asyncio.start_server(client_connected_cb=self.client_connected, host=host, port=port)

        async with server:
            await server.serve_forever()
    
    async def client_connected(self, reader: StreamReader, writer: StreamWriter) -> None:
        command = await reader.readline()
        print(f'CONNECTED {reader} {writer}')
        command, args = command.split(sep=b' ')
        if command == b'CONNECT':
            username = args.replace(b'\n', b'').decode()
            self._add_user(username=username, reader=reader, writer=writer)
            await self._on_connect(username=username, writer=writer)
        else:
            logging.error(msg='Got an unsupporter command from the client, disconnecting.')
            writer.close()
            await writer.wait_closed()

    def _add_user(self, username: str, reader: StreamReader, writer: StreamWriter) -> None:
        self._username_to_writer[username] = writer
        asyncio.create_task(coro=self._listen_for_messages(username=username, reader=reader))

    async def _on_connect(self, username: str, writer: StreamWriter) -> None:
        writer.write(data=f'Welcome! Total users: {len(self._username_to_writer)}.\n'.encode()); await writer.drain()
        await self._notify_all(message=f'{username} has been connected.\n')

    async def _remove_user(self, username: str) -> None:
        writer = self._username_to_writer[username]
        del self._username_to_writer[username]
        try:
            writer.close()
            await writer.wait_closed()
        except BaseException as error:
            logging.exception(msg=f'Error closing the client\'s writer, ignoring.', exc_info=error)

    async def _listen_for_messages(self, username: str, reader: StreamReader) -> None:
        try:
            while (data := await asyncio.wait_for(fut=reader.readline(), timeout=60)) != b'':
                await self._notify_all(message=f'{username}: {data.decode()}')
            await self._notify_all(message=f'{username} has left the chat.\n')
        except BaseException as error:
            logging.exception(msg=f'Error reading the data from the client.', exc_info=error)
            await self._remove_user(username=username)

    async def _notify_all(self, message: str) -> None:
        inactive_users = list()
        for username, writer in self._username_to_writer.items():
            try:
                writer.write(data=message.encode()); await writer.drain()
            except ConnectionError as error:
                logging.exception(msg=f'Error writing the data to the client.', exc_info=error)
                inactive_users.append(username)
        [await self._remove_user(username=username) for username in inactive_users]


async def main() -> None:
    chat_server = ChatServer()
    await chat_server.start_chat_server(host='127.0.0.1', port=8000)


if __name__ == '__main__':
    asyncio.run(main=main())