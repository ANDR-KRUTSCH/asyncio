import asyncio, socket
from socket import socket as Socket
from types import TracebackType


class ConnectedSocket:
    
    def __init__(self, server_socket: Socket) -> None:
        self._connection: Socket | None = None
        self._server_socket = server_socket

    async def __aenter__(self) -> Socket:
        print('There is the enter to the async context manager, waiting for the connection.')
        loop = asyncio.get_event_loop()
        connection, address = await loop.sock_accept(sock=self._server_socket)
        self._connection = connection
        print('The connection was created.')
        return self._connection
    
    async def __aexit__(self, exc_type: type[BaseException], exc_val: BaseException, exc_tb: TracebackType):
        print('There is the exit from the async context manager.')
        self._connection.close()
        print('The connection was closed.')


async def main() -> None:
    loop = asyncio.get_event_loop()
    
    server_socket = Socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)

    server_socket.setblocking(False)
    
    server_socket.listen()

    async with ConnectedSocket(server_socket=server_socket) as connection:
        data = await loop.sock_recv(connection, 1024)
        print(data)


if __name__ == '__main__':
    asyncio.run(main=main())