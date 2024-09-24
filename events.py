import asyncio


class FileUpload:

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self._reader: asyncio.StreamReader = reader
        self._writer: asyncio.StreamWriter = writer
        self._finished: asyncio.Event = asyncio.Event()
        self._buffer = bytes()
        self._upload: asyncio.Task = None

    def listen_for_uploads(self) -> None:
        self._upload = asyncio.create_task(coro=self._accept_upload())

    async def _accept_upload(self) -> None:
        while data := await self._reader.read(1024):
            self._buffer += data
        
        self._finished.set()
        self._writer.close(); await self._writer.wait_closed()

    async def get_contents(self) -> bytes:
        await self._finished.wait()
        return self._buffer
    

class FileServer:

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.upload: asyncio.Event = asyncio.Event()

    async def start_server(self) -> None:
        server = await asyncio.start_server(client_connected_cb=self._client_connected, host=self.host, port=self.port)
        print('Server has been started. Starting accepting connections...')
        await server.serve_forever()

    async def dump_contents_on_complete(self, upload: FileUpload) -> None:
        print(await upload.get_contents())

    def _client_connected(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        upload = FileUpload(reader=reader, writer=writer)
        print('Client has been connected. Listening for uploads...')
        upload.listen_for_uploads()
        asyncio.create_task(coro=self.dump_contents_on_complete(upload=upload))
    

async def main() -> None:
    server = FileServer(host='127.0.0.1', port=8000)
    await server.start_server()


if __name__ == '__main__':
    asyncio.run(main=main())