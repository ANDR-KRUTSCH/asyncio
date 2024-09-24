import asyncio


async def do_work(condition: asyncio.Condition) -> None:
    while True:
        print('Waiting for the lock of the condition...')
        async with condition:
            print('The lock of the condition has been gotten. Waiting for the condition...')
            await condition.wait()
            print('The condition has been completed, the lock of the condition has been gotten. Working...')
            await asyncio.sleep(delay=1)
        print('The work has been completed. The lock of the conditions has been left.')

async def fire_event(condition: asyncio.Condition) -> None:
    while True:
        await asyncio.sleep(delay=5)
        print('Before the notifying, getting the lock of the condition.')
        async with condition:
            print('The lock of the condition has been gotten. Notifying...')
            condition.notify_all()
        print('The end of the notifying. The lock of the condition has been left.')

async def main() -> None:
    condition = asyncio.Condition()

    asyncio.create_task(coro=fire_event(condition=condition))

    await asyncio.gather(do_work(condition=condition), do_work(condition=condition))


if __name__ == '__main__':
    asyncio.run(main=main())