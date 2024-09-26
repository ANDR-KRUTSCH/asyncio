import asyncio
from asyncio.subprocess import Process


async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('sleep', '3')
    try: print('status:', await asyncio.wait_for(fut=process.wait(), timeout=1))
    except TimeoutError:
        process.terminate()
        print('status:', await process.wait())

if __name__ == '__main__':
    asyncio.run(main=main())