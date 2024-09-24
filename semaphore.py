import asyncio, aiohttp


async def get_url(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> int:
    print('Waiting for the opportunity to get semaphore.')
    async with semaphore:
        print('The semaphore has been got.')
        response = await session.get(url=url)
        print('The request has been completed.')
        return response.status

async def main() -> None:
    semaphore = asyncio.Semaphore(value=10)
    async with aiohttp.ClientSession() as session:
        tasks = [get_url(url='https://www.example.com', session=session, semaphore=semaphore) for _ in range(100)]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main=main())