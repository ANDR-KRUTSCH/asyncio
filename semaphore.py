import asyncio


async def acquire(semaphore: asyncio.Semaphore) -> None:
    print('Waiting for the semaphore...')
    async with semaphore:
        print('The semaphore has been got.')
        await asyncio.sleep(delay=1)
    print('The semaphore has been left.')

async def release(semaphore: asyncio.Semaphore) -> None:
    print('Single lefting...')
    semaphore.release()
    print('Single lefting has been complete.')

async def main() -> None:
    semaphore = asyncio.BoundedSemaphore(value=2)

    print('2 gets, 3 lefts.')
    await asyncio.gather(acquire(semaphore=semaphore), acquire(semaphore=semaphore), release(semaphore=semaphore))

    print('3 gets.')
    await asyncio.gather(acquire(semaphore=semaphore), acquire(semaphore=semaphore), acquire(semaphore=semaphore))


if __name__ == '__main__':
    asyncio.run(main=main())