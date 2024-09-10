import asyncio, sys, shutil
from asyncio import StreamReader, StreamReaderProtocol
from collections import deque as Deque
from typing import Callable, Awaitable


class MessageStore:

    def __init__(self, callback: Callable[[Deque], Awaitable[None]], max_size: int) -> None:
        self._deque = Deque(maxlen=max_size)
        self._callback = callback

    async def append(self, message: str) -> None:
        self._deque.append(message)
        await self._callback(self._deque)


async def create_stdin_reader() -> StreamReader:
    stream_reader = StreamReader()
    await asyncio.get_running_loop().connect_read_pipe(protocol_factory=lambda: StreamReaderProtocol(stream_reader=stream_reader), pipe=sys.stdin)
    return stream_reader

def select_first_line(max_size: int) -> None:
    sys.stdout.write(f'\033[{max_size}A'); sys.stdout.flush()
    sys.stdout.write('\033[0G'); sys.stdout.flush()

def select_last_line() -> int:
    _, max_size = shutil.get_terminal_size()
    sys.stdout.write(f'\033[{max_size}B'); sys.stdout.flush()
    return max_size

def clear_selected_line() -> None:
    sys.stdout.write('\033[K'); sys.stdout.flush()

buffer = Deque()

BACKSPACE = b'\x7f'

def backspace() -> None:
    '''This method removes the last symbol of the entering command.'''

    # Move cursor to the begin of the line.
    sys.stdout.write('\033[0G'); sys.stdout.flush()
    # Clear the line.
    sys.stdout.write('\033[K'); sys.stdout.flush()
    # Remove the last symbol in the buffer. If it is empty then do nothing.
    if len(buffer) > 0: buffer.pop()
    # Display the buffer.
    result = b''.join(buffer)
    sys.stdout.write(result.decode()); sys.stdout.flush()

async def reader(stdin_reader: StreamReader) -> int:
    '''This method processes the user's input in the CMD.'''

    while True:
        key: bytes = await stdin_reader.read(1)

        if key == b'\n':
            if len(buffer) == 0: raise ValueError()
            else:
                try: result = b''.join(buffer) # int(b''.join(buffer))
                except: raise ValueError()
                else: return result.decode() # return result
                finally: buffer.clear()
        else:
            if key == BACKSPACE: backspace()
            else: buffer.append(key); sys.stdout.write(key.decode()); sys.stdout.flush()