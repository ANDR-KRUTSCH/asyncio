import asyncio, os, tty, sys, logging
from asyncio import StreamReader, StreamWriter
from collections import deque as Deque
from util import MessageStore, read, select_first_line, select_last_line, clear_selected_line, create_stdin_reader


async def send_message(message: str, writer: StreamWriter) -> None:
    writer.write(data=(message + '\n').encode()); await writer.drain()

async def listen_for_messages(reader: StreamReader, message_store: MessageStore) -> None:
    while (message := await reader.readline()) != b'': await message_store.append(message=message.decode())
    await message_store.append(message='Server closed the connection.')

async def read_and_send(stdin_reader: StreamReader, writer: StreamWriter) -> None:
    while True:
        message = await read(stdin_reader=stdin_reader)
        await send_message(message=message, writer=writer)

async def main() -> None:
    os.system(command='clear')
    tty.setcbreak(fd=sys.stdin.fileno())

    max_size = select_last_line()

    async def update_stdout(deque: Deque) -> None:
        select_first_line(max_size=max_size)

        for message in deque:
            print(message, end='')

        select_last_line()
        clear_selected_line()

    message_store = MessageStore(callback=update_stdout, max_size=max_size)

    stdin_reader = await create_stdin_reader()

    sys.stdout.write('Input username: '); sys.stdout.flush()
    username = await read(stdin_reader=stdin_reader)

    reader, writer = await asyncio.open_connection(host='127.0.0.1', port=8000)

    writer.write(data=f'CONNECT {username}\n'.encode()); await writer.drain()

    message_listener = asyncio.create_task(coro=listen_for_messages(reader=reader, message_store=message_store))

    input_listener = asyncio.create_task(coro=read_and_send(stdin_reader=stdin_reader, writer=writer))

    try:
        await asyncio.wait(fs=[message_listener, input_listener], return_when=asyncio.FIRST_COMPLETED)
    except BaseException as error:
        logging.exception(error)
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(main=main())