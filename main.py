import asyncio, requests, time


async def main() -> None:
    loop = asyncio.get_running_loop(); tasks = list()

    start = time.time()

    for _ in range(10): tasks.append(asyncio.to_thread(lambda url: requests.get(url=url).status_code, 'https://www.example.com'))

    result = await asyncio.gather(*tasks)

    print(result)

    end = time.time()

    print(f'{end - start:.4f}')


if __name__ == '__main__':
    asyncio.run(main=main())