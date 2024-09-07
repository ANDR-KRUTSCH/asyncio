import threading, socket
from socket import socket as Socket


class ClientEchoThread(threading.Thread):

    def __init__(self, client: Socket) -> None:
        super().__init__()
        self.client = client

    def run(self) -> None:
        try:
            while True:
                if not (data := self.client.recv(2048)): raise BrokenPipeError('Connection closed!')
                else: print(f'Received: {data}'); self.client.sendall(data)
        except OSError as error: print(f'Thread was interrupt by exception: {error}')

    def close(self) -> None:
        if self.is_alive(): self.client.sendall(b'Stopping!'); self.client.shutdown(socket.SHUT_RDWR)

with Socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('127.0.0.1', 8000))
    
    server.listen()

    connection_threads: list[ClientEchoThread] = list()

    try:
        while True:
            connection, address = server.accept()
            connection_threads.append((thread := ClientEchoThread(client=connection)))
            thread.start()
    except KeyboardInterrupt:
        print('Stopping!')
        [thread.close() for thread in connection_threads]