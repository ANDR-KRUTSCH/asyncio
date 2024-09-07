import asyncio, aiohttp, threading, logging
from asyncio import AbstractEventLoop
from concurrent.futures import Future
from tkinter import ttk, Tk, Label, Entry
from queue import Queue
from typing import Callable


class LoadTester(Tk):

    def __init__(self, loop: AbstractEventLoop, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Create the queue. It will accept the data from the asyncio's thread.
        self._queue = Queue()

        self._refresh_ms = 25

        self._loop = loop
        self._load_test: StressTest | None = None
        
        self.title(string='URL Requester')

        Label(master=self, text='URL:').grid(row=0, column=0)

        self._url_field = Entry(master=self, width=10)
        self._url_field.grid(row=0, column=1)

        Label(master=self, text='Number of requests:').grid(row=1, column=0)

        self._request_field = Entry(master=self, width=10)
        self._request_field.grid(row=1, column=1)

        Label(master=self, text='Progress:').grid(row=2, column=0)

        self._pb = ttk.Progressbar(master=self, orient='horizontal', length=83, mode='determinate')
        self._pb.grid(row=2, column=1)

        self._submit = ttk.Button(master=self, text='Submit', command=self._start)
        self._submit.grid(row=4, column=1)

        print('The Tk-app has been successfully initialized and started.')

    def _update_bar(self, pct: int) -> None:
        self._pb['value'] = pct
        if pct == 100:
            self._load_test = None
            self._submit['text'] = 'Submit'
        else:
            self.after(self._refresh_ms, self._poll_queue)

    def _queue_update(self, completed_requests: int, total_requests: int) -> None:
        print('Updating of the queue...')
        self._queue.put(item=int(completed_requests / total_requests * 100))
        print('The queue has been updated.')

    def _poll_queue(self) -> None:
        if not self._queue.empty():
            pct = self._queue.get()
            print(f'Current progress: {pct}')
            self._update_bar(pct=pct)
        else:
            if self._load_test: self.after(ms=self._refresh_ms, func=self._poll_queue)

    def _start(self) -> None:
        if self._load_test is None:
            self._submit['text'] = 'Cancel'
            self._load_test = StressTest(loop=self._loop, url=self._url_field.get(), total_requests=int(self._request_field.get()), callback=self._queue_update)
            self.after(ms=self._refresh_ms, func=self._poll_queue)
            self._load_test.start()
        else:
            self._load_test.cancel()
            self._load_test = None
            self._submit['text'] = 'Submit'


class StressTest:

    def __init__(self, loop: AbstractEventLoop, url: str, total_requests: int, callback: Callable[[int, int], None]) -> None:
        self._completed_requests = 0
        self._load_test_future: Future | None = None
        self._loop = loop
        self._url = url
        self._total_requests = total_requests
        self._callback = callback
        self._refresh_rate = total_requests // 100

    def start(self) -> None:
        self._load_test_future = asyncio.run_coroutine_threadsafe(coro=self._make_requests(), loop=self._loop)

    def cancel(self) -> None:
        print('Canceling of sending the requests...')
        if self._load_test_future: self._loop.call_soon_threadsafe(self._load_test_future.cancel)
        print('Sending the requests has been canceled.')

    async def _get_url(self, session: aiohttp.ClientSession, url: str) -> None:
        try: 
            response = await session.get(url=url)
            print(response.status)
        except BaseException as exception: pass #logging.exception(exception)
        self._completed_requests += 1
        self._callback(self._completed_requests, self._total_requests)

    async def _make_requests(self) -> None:
        print('Creating of the client-session...')
        async with aiohttp.ClientSession() as session:
            print('The client-session has been created.')
            print('Creating of the requests\' collection...')
            reqs = [self._get_url(session=session, url=self._url) for _ in range(self._total_requests)]
            print(f'The requests\' collection has been created. Sending the {self._total_requests} request(s) to URL: "{self._url}"...')
            await asyncio.gather(*reqs)
            print('All the requests have been send.')


class ThreadEventLoop(threading.Thread):

    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self.daemon = True

    def run(self) -> None:
        self._loop.run_forever()


if __name__ == '__main__':
    # 1. Create the asyncio's event-loop.
    print('Creating the new asyncio\'s event-loop...')
    loop = asyncio.new_event_loop()
    print('The asyncio\'s event-loop has been successfully created.')
    # 2. Create and run the thread where will work asyncio's event-loop.
    print('Initializing of the thread for the asyncio\'s event-loop...')
    ThreadEventLoop(loop=loop).start()
    print('The thread for the asyncio\'s event-loop has been successfully initialized and started.')
    # 3. Create the Tk-app and run it's event-loop.
    print('Initializing of the Tk-app and starting...')
    LoadTester(loop=loop).mainloop()
    print('The Tk-app has been closed.')