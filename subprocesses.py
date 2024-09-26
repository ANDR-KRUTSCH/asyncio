import asyncio
from asyncio.subprocess import Process, PIPE


async def write_output(prefix: str, stdout: asyncio.StreamReader) -> None:
    while line := await stdout.readline():
        print(f'[{prefix}]: {line.rstrip().decode()}')

async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('ls', '-l', stdout=PIPE)
    stdout_task = asyncio.create_task(coro=write_output(prefix='ls -l', stdout=process.stdout))

    code, _ = await asyncio.gather(process.wait(), stdout_task)
    print('status:', code)


if __name__ == '__main__':
    asyncio.run(main=main())