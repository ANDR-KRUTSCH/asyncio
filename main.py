import asyncio, os, tty, sys
from collections import deque as Deque
from util import MessageStore, reader, select_last_line, select_first_line, clear_selected_line, create_stdin_reader


async def main() -> None:
    os.system(command='clear')
    tty.setcbreak(fd=sys.stdin.fileno())

    max_size = select_last_line()

    async def sleep(delay: int, message_store: MessageStore) -> None:
        await message_store.append(message=f'Sleeping for {delay} second(s) started...')
        await asyncio.sleep(delay=delay)
        await message_store.append(message=f'Sleeping for {delay} second(s) finished.')

    async def update_stdout(deque: Deque) -> None:
        select_first_line(max_size=max_size)

        for message in deque:
            print(message)

        select_last_line()
        clear_selected_line()

    message_store = MessageStore(callback=update_stdout, max_size=max_size)

    stdin_reader = await create_stdin_reader()

    while True:
        delay = await reader(stdin_reader=stdin_reader)
        asyncio.create_task(coro=sleep(delay=delay, message_store=message_store))


if __name__ == '__main__':
    asyncio.run(main=main())