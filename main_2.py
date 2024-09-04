import asyncio, aiohttp
from util import fetch_status


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        task_1 = asyncio.create_task(fetch_status(session=session, url='https://www.example.com', delay=1))
        task_2 = asyncio.create_task(fetch_status(session=session, url='https://www.example.com', delay=5))

        done, pendding = await asyncio.wait(fs=[task_1, task_2], timeout=3)

        print(f'Done tasks: {len(done)}')
        print(f'Pendding tasks: {len(pendding)}')

        for task in done:
            result = await task
            print(result)

        for task in pendding:
            if task == task_2:
                print('<task_2> was canceled.')
                task.cancel()


if __name__ == '__main__':
    asyncio.run(main=main())