import asyncio


async def processer(queue: asyncio.Queue) -> None:
    while not queue.empty():
        item: tuple[int, str] = await queue.get(); print(f'Element: "{item}". Processing...')
        queue.task_done()

async def main() -> None:
    priority_queue = asyncio.PriorityQueue()

    items = [
        (3, 'Low'),
        (2, 'Medium'),
        (1, 'High'),
    ]

    processer_task = asyncio.create_task(coro=processer(queue=priority_queue))

    for item in items:
        priority_queue.put_nowait(item)

    await asyncio.gather(priority_queue.join(), processer_task)


if __name__ == '__main__':
    asyncio.run(main=main())