import asyncio, aiohttp, logging
from bs4 import BeautifulSoup


class SourceProcesser:

    def __init__(self, url: str, depth: int) -> None:
        self.url = url
        self.depth = depth


async def processer(id: int, queue: asyncio.Queue, session: aiohttp.ClientSession, max_depth: int) -> None:
    print(f'Processer({id})')
    while True:
        source_processer: SourceProcesser = await queue.get()
        print(f'Processer({id}): processes url="{source_processer.url}"')
        await process_source(source_processer=source_processer, queue=queue, session=session, max_depth=max_depth)
        queue.task_done()

async def process_source(source_processer: SourceProcesser, queue: asyncio.Queue, session: aiohttp.ClientSession, max_depth: int) -> None:
    try:
        response = await session.get(url=source_processer.url, timeout=3)
        if source_processer.depth == max_depth:
            print(f'Max depth for url="{source_processer.url}"')
        else:
            body = await response.text()
            
            beautiful_soup = BeautifulSoup(markup=body, features='html.parser')
            
            links = beautiful_soup.find_all(name='a', href=True)
            for link in links:
                queue.put_nowait(SourceProcesser(url=link['href'], depth=source_processer.depth + 1))
    except BaseException:
        logging.exception(f'Error when processing url="{source_processer.url}"')


async def main() -> None:
    queue = asyncio.Queue()

    queue.put_nowait(SourceProcesser(url='https://www.example.com', depth=0))

    async with aiohttp.ClientSession() as session:
        processers = [asyncio.create_task(coro=processer(id=id, queue=queue, session=session, max_depth=3)) for id in range(2)]

        await queue.join()

        [processer.cancel() for processer in processers]


if __name__ == '__main__':
    asyncio.run(main=main())