import asyncio
from asyncio.subprocess import Process, PIPE


async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('python', 'temp.py', stdout=PIPE)

    stdout, stderr = await process.communicate()

    print(stdout); print(stderr)

    print('status:', process.returncode)


if __name__ == '__main__':
    asyncio.run(main=main())