import asyncio
from util import delay


async def create_task_no_sleep() -> None:
    task_1 = asyncio.create_task(coro=delay(delay_seconds=1))
    task_2 = asyncio.create_task(coro=delay(delay_seconds=2))

    await asyncio.gather(task_1, task_2)

async def create_task_sleep() -> None:
    task_1 = asyncio.create_task(coro=delay(delay_seconds=1))
    await asyncio.sleep(delay=0)
    task_2 = asyncio.create_task(coro=delay(delay_seconds=2))
    await asyncio.sleep(delay=0)
    await asyncio.gather(task_1, task_2)

async def main() -> None:
    await create_task_sleep()


if __name__ == '__main__':
    asyncio.run(main=main())