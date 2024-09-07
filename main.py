import asyncio, hashlib, os, string, functools, time, random
from concurrent.futures import ThreadPoolExecutor
from util import async_timed


def random_password(length: int) -> bytes:
    ascii_lowercase = string.ascii_lowercase.encode()
    return b''.join(bytes(random.choice(ascii_lowercase)) for _ in range(length))

def hash(password: bytes) -> str:
    salt = os.urandom(16)
    return str(hashlib.scrypt(password=password, salt=salt, n=2048, p=1, r=8))

passwords = [random_password(length=10) for _ in range(1000)]

@async_timed()
async def main() -> None:
    loop = asyncio.get_running_loop(); tasks = list()

    with ThreadPoolExecutor() as executor:
        for password in passwords: tasks.append(loop.run_in_executor(executor=executor, func=functools.partial(hash, password)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main=main())