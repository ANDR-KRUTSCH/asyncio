import asyncio, dataclasses


@dataclasses.dataclass(order=True)
class Item:
    priority: int
    order: int
    data: str = dataclasses.field(compare=False)


async def processer(queue: asyncio.Queue) -> None:
    while not queue.empty():
        item: Item = await queue.get(); print(f'Item({item}). Processing...')
        queue.task_done()

async def main() -> None:
    lifo_queue = asyncio.LifoQueue()

    items = [
        Item(priority=3, order=1, data='Lowest 1'),
        Item(priority=3, order=2, data='Lowest 2'),
        Item(priority=3, order=3, data='Lowest 3'),
        Item(priority=2, order=4, data='Medium'),
        Item(priority=1, order=5, data='High'),
    ]

    for item in items:
        lifo_queue.put_nowait(item=item)

    processer_task = asyncio.create_task(coro=processer(queue=lifo_queue))

    await asyncio.gather(lifo_queue.join(), processer_task)


if __name__ == '__main__':
    asyncio.run(main=main())