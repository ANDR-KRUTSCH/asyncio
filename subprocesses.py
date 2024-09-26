import asyncio
from asyncio.subprocess import Process


async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('ls', '-l')
    print(f'PID: {process.pid}')
    print('status:', await process.wait())


if __name__ == '__main__':
    asyncio.run(main=main())