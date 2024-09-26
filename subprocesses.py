import asyncio
from asyncio.subprocess import Process, PIPE


async def stdout_reader(stdout: asyncio.StreamReader, input_ready_event: asyncio.Event) -> None:
    while (data := await stdout.read(1024)) != b'':
        print(data)
        if data.decode().endswith('-> '): input_ready_event.set()

async def stdin_writer(stdin: asyncio.StreamWriter, input_ready_event: asyncio.Event, texts: list[str]) -> None:
    for text in texts:
        await input_ready_event.wait()
        stdin.write(data=text.encode()); await stdin.drain()
        input_ready_event.clear()

async def main() -> None:
    process: Process = await asyncio.create_subprocess_exec('python', 'programm.py', stdin=PIPE, stdout=PIPE)

    input_ready_event = asyncio.Event()

    texts = ['one\n', 'two\n', 'three\n', 'quit\n']

    await asyncio.gather(stdout_reader(stdout=process.stdout, input_ready_event=input_ready_event), stdin_writer(stdin=process.stdin, input_ready_event=input_ready_event, texts=texts), process.wait())


if __name__ == '__main__':
    asyncio.run(main=main())