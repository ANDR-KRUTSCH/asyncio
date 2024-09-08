import asyncio
from asyncio import StreamReader
from typing import AsyncGenerator


async def read_until_empty(stream_reader: StreamReader) -> AsyncGenerator[str, None]:
    while response := await stream_reader.readline():
        yield response.decode()

async def main():
    stream_reader, stream_writer = await asyncio.open_connection(host='www.example.com', port=80)

    try:
        stream_writer.write(data='GET / HTTP/1.1\r\nConnection: close\r\nHost www.example.com\r\n\r\n'.encode())
        await stream_writer.drain()

        responses = [response async for response in read_until_empty(stream_reader=stream_reader)]

        print(''.join(responses))
    finally:
        stream_writer.close()
        await stream_writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(main=main())