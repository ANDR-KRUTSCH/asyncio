import asyncio, socket, signal, logging
from asyncio import AbstractEventLoop, Task, TimeoutError
from socket import socket as Socket


async def echo(connection: Socket, loop: AbstractEventLoop) -> None:
    # 8. Wait for incomming the data from client. If client send "boom", raise the exception else sent the data back to the client and close the connection anyway in the end. 
    try:
        while data := await loop.sock_recv(connection, 1024):
            if data == b'boom\r\n': raise Exception('Unxpected network error!')
            else: await loop.sock_sendall(sock=connection, data=data)
    except Exception as ex:
        logging.exception(msg=ex)
    finally:
        connection.close()

echo_tasks = list()

async def connection_listener(server_socket: Socket, loop: AbstractEventLoop) -> None:
    while True:
        # 6. Wait for the connection from the client.
        connection, address = await loop.sock_accept(sock=server_socket)
        connection.setblocking(False)
        print(f'There is the request for connecting from {address}')
        # 7. Create task for the "echo" coroutine with the client socket.
        echo_tasks.append(asyncio.create_task(coro=echo(connection=connection, loop=loop)))

class GracefulExit(SystemExit):
    pass

def shutdown():
    raise GracefulExit()

async def close_echo_tasks(echo_tasks: list[Task]):
    # 9. Let tasks complete their work for 2 seconds.
    waiters = [asyncio.wait_for(fut=task, timeout=2) for task in echo_tasks]
    for task in waiters:
        try:
            await task
        except TimeoutError:
            pass

# 1. Create an event loop.
loop = asyncio.get_event_loop()

async def main() -> None:
    # 3. Create the server socket, that will be accepting the requests for connecting from clients.
    # AF_INET - use hostname and port; SOCK_STREAM - use TCP.
    server_socket = Socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    # Use the same port every time.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('127.0.0.1', 8000)
    server_socket.bind(server_address)
    server_socket.setblocking(False)
    server_socket.listen()

    # 4. If there were CTRL+C or kill commands, then run "shutdown" function, that will raise the "GracefulExit" exception.
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(sig=getattr(signal, signame), callback=shutdown)

    # 5. Run the "connection_listener" coroutine.
    await connection_listener(server_socket=server_socket, loop=asyncio.get_event_loop())

# 2. Try to execute until complete the "main" coroutine in the event loop.
# If the "GracefulExit" exception was raised, then execute until complete "close_echo_tasks" coroutine.
# Anyway, close the event loop in the end.
try:
    loop.run_until_complete(future=main())
except GracefulExit:
    loop.run_until_complete(future=close_echo_tasks(echo_tasks=echo_tasks))
finally:
    loop.close()