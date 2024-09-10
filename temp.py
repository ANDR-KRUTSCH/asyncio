import asyncio, asyncpg, os, tty, sys, decouple
from asyncpg import Pool, Connection
from collections import deque as Deque
from util import MessageStore, reader, select_last_line, select_first_line, clear_selected_line, create_stdin_reader


async def run_query(query: str, pool: Pool, message_store: MessageStore) -> None:
    async with pool.acquire() as connection:
        connection: Connection
        try:
            result = await connection.fetchrow(query=query)
            await message_store.append(message=f'{len(result)} rows selected by the query: {query}')
        except BaseException as error:
            await message_store.append(message=f'Got an exception from the query: {query}')

async def main() -> None:
    os.system(command='clear')
    tty.setcbreak(fd=sys.stdin.fileno())

    max_size = select_last_line()

    async def update_stdout(deque: Deque) -> None:
        select_first_line(max_size=max_size)

        for message in deque:
            print(message)

        select_last_line()
        clear_selected_line()

    message_store = MessageStore(callback=update_stdout, max_size=max_size)

    stdin_reader = await create_stdin_reader()

    async with asyncpg.create_pool(host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database='products', min_size=6, max_size=6) as pool:
        while True:
            query = await reader(stdin_reader=stdin_reader)
            asyncio.create_task(coro=run_query(query=query, pool=pool, message_store=message_store))


if __name__ == '__main__':
    asyncio.run(main=main())