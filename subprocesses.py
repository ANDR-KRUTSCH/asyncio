import asyncio, random, string, os, time
from asyncio.subprocess import Process, PIPE


async def encrypt(semaphore: asyncio.Semaphore, text: str) -> bytes:
    programm = ['gpg', '-c', '--batch', '--passphrase', '3ncryptm3', '--cipher-algo', 'TWOFISH'] # gpg -c --batch --passphrase 3ncryptm3 --cipher-algo TWOFISH

    async with semaphore:
        process: Process = await asyncio.create_subprocess_exec(*programm, stdin=PIPE, stdout=PIPE)

        stdout, stderr = await process.communicate(input=text.encode())

        return stdout

async def main() -> None:
    texts = [''.join(random.choice(string.ascii_letters) for _ in range(1000)) for _ in range(1000)]

    semaphore = asyncio.Semaphore(value=os.cpu_count())

    start = time.time()

    tasks = [asyncio.create_task(coro=encrypt(semaphore=semaphore, text=text)) for text in texts]

    await asyncio.gather(*tasks)

    end = time.time()

    print(f'time: {end-start:.4f} second(s)')


if __name__ == '__main__':
    asyncio.run(main=main())