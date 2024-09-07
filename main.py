import asyncio, requests
from threading import Lock
from util import async_timed


counter_lock = Lock()
counter = 0

def get_status_code(url: str) -> int:
    global counter

    response = requests.get(url=url)

    with counter_lock:
        counter += 1

    return response.status_code

async def reporter(requests_count: int) -> None:
    while counter < requests_count:
        print(f'{counter}/{requests_count}')
        await asyncio.sleep(0.5)

@async_timed()
async def main(requests_count: int) -> None:
    loop = asyncio.get_running_loop()
    
    tasks = [asyncio.to_thread(get_status_code, 'https://www.example.com') for _ in range(requests_count)]
    reporter_task = asyncio.create_task(coro=reporter(requests_count=requests_count))

    result = await asyncio.gather(*tasks)

    await reporter_task

    print(result)


if __name__ == '__main__':
    asyncio.run(main=main(requests_count=200))