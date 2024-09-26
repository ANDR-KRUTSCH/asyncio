import asyncio
from asyncio.subprocess import Process, PIPE


async def consume_and_send(texts: list[str], stdin: asyncio.StreamWriter, stdout: asyncio.StreamReader) -> None:
    for text in texts:
        print(await stdout.read(2048))
        stdin.write(text.encode()); await stdin.drain()

async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('python', 'programm.py', stdin=PIPE, stdout=PIPE)

    texts = ['one\n', 'two\n', 'three\n', 'quit\n']

    await asyncio.gather(consume_and_send(texts=texts, stdout=process.stdout, stdin=process.stdin), process.wait())


if __name__ == '__main__':
    asyncio.run(main=main())