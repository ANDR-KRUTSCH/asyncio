import asyncio, typing


class TaskExecutor:

    def __init__(self) -> None:
        self.event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.tasks: list[typing.Coroutine | typing.Callable] = list()

    def add_task(self, callback: typing.Coroutine | typing.Callable) -> None:
        if not isinstance(callback, typing.Coroutine) and not isinstance(callback, typing.Callable): raise TypeError()
        else: self.tasks.append(callback)

    async def _run(self) -> None:
        awaitable_tasks: list[asyncio.Task] = list()

        for task in self.tasks:
            if asyncio.iscoroutine(obj=task): awaitable_tasks.append(asyncio.create_task(coro=task))
            elif asyncio.iscoroutinefunction(func=task): awaitable_tasks.append(asyncio.create_task(coro=task()))
            else: self.event_loop.call_soon(callback=task)

        await asyncio.gather(*awaitable_tasks)

    def run(self) -> None:
        self.event_loop.run_until_complete(future=self._run())


if __name__ == '__main__':
    def func() -> None:
        print('func')

    async def coro() -> None:
        await asyncio.sleep(delay=2)
        print('coro')

    task_executor = TaskExecutor()

    task_executor.add_task(callback=coro())
    task_executor.add_task(callback=coro)
    task_executor.add_task(callback=func)

    task_executor.run()