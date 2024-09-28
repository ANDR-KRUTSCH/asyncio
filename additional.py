import selectors, functools, socket
from socket import socket as Socket
from typing import Callable, Any, Coroutine


class Future:

    def __init__(self) -> None:
        self._done: bool = False
        self._done_callback: Callable[[Any], Any] = None
        self._result: Any = None

    def done(self) -> bool:
        return self._done
    
    def add_done_callback(self, fn: Callable[[Any], Any]) -> None:
        if not isinstance(fn, Callable): raise TypeError()
        else: self._done_callback = fn
    
    def set_result(self, result: Any) -> None:
        self._result = result
        self._done = True
        if self._done_callback: self._done_callback(result)

    def result(self) -> Any:
        return self._result

    def __await__(self):
        if self.done(): return self.result()
        else: yield self


class Task(Future):

    def __init__(self, coro: Coroutine, loop) -> None:
        super(Task, self).__init__()
        self._coro: Coroutine = coro
        self._loop = loop
        self._state: Any = None
        self._result: Any = None
        self._loop.register_task(self)
    
    def step(self) -> None:
        try:
            if self._state is None: self._state = self._coro.send(None)
            if isinstance(self._state, Future): self._state.add_done_callback(fn=self._future_done)
        except StopIteration as stop_iteration:
            self.set_result(result=stop_iteration.value)

    def _future_done(self, result: Any) -> None:
        self._result = result
        try:
            self._state = self._coro.send(self._result)
        except StopIteration as stop_iteration:
            self.set_result(result=stop_iteration.value)


class EventLoop:
    
    def __init__(self) -> None:
        self.selector = selectors.DefaultSelector()
        self._tasks: list[Task] = list()
        self._result: Any = None

    def _register_socket(self, sock: Socket, callback: Callable[[Future, Socket], Any]) -> Future:
        future = Future()

        # Проверка регистрации сокета.
        try:
            self.selector.get_key(fileobj=sock)
        # Если сокет не зарегистрирован в селекторе.
        except KeyError:
            sock.setblocking(False)
            self.selector.register(fileobj=sock, events=selectors.EVENT_READ, data=functools.partial(callback, future))
        # Если сокет зарегистрирован, осуществляется замена функции обратного вызова.
        else:
            self.selector.modify(fileobj=sock, events=selectors.EVENT_READ, data=functools.partial(callback, future))
        
        return future
        
    def _set_result(self, result: Any) -> None:
        self._result = result

    async def sock_recv(self, client_socket: Socket):
        print('Регистрация клиентского сокета для прослушивания входящих данных...')
        future: Future = self._register_socket(sock=client_socket, callback=self.recieved_data)
        await future
        return future.result()
    
    async def sock_accept(self, server_socket: Socket):
        print('Регистрация серверного сокета для приёма подключений...')
        future: Future = self._register_socket(sock=server_socket, callback=self.accept_connection)
        await future
        return future.result()
    
    def sock_close(self, sock: Socket) -> None:
        self.selector.unregister(fileobj=sock)
        sock.close()
    
    def register_task(self, task: Task) -> None:
        self._tasks.append(task)

    def recieved_data(self, future: Future, client_socket: Socket) -> None:
        future.set_result(result=client_socket.recv(1024))

    def accept_connection(self, future: Future, server_socket: Socket) -> None:
        future.set_result(result=server_socket.accept())

    def run(self, main: Coroutine) -> None:
        self._result = main.send(None)

        while True:
            try:
                if isinstance(self._result, Future):
                    self._result.add_done_callback(fn=self._set_result)
                    if self._result.result() is not None: self._result = main.send(self._result.result())
                else: self._result = main.send(self._result)
            except StopIteration as stop_iteration:
                return stop_iteration.value
            
            for task in self._tasks: task.step()

            self._tasks = [task for task in self._tasks if not task.done()]

            events = self.selector.select()

            print('В селекторе имеется событие. Обработка...')

            for key, _ in events:
                callback = key.data
                callback(key.fileobj)


async def read_from_client(client_socket: Socket, loop: EventLoop) -> None:
    print(f'Чтение данных от клиента {client_socket}')
    try:
        while data := await loop.sock_recv(client_socket=client_socket):
            print(f'Получены данные от клиента: <{data}>')
    finally:
        loop.sock_close(sock=client_socket)

async def listen_for_connections(server_socket: Socket, loop: EventLoop) -> None:
    while True:
        print('Ожидание подключений...')
        client_socket, address = await loop.sock_accept(server_socket=server_socket)
        Task(coro=read_from_client(client_socket=client_socket, loop=loop), loop=loop)
        print(f'Зарегистрировано подключение.')

async def main(loop: EventLoop) -> None:
    # Создание серверного сокета.
    # socket.AF_INET: указывает использование адресации IPv4; socket.SOCK_STREAM: указывает использование TCP.
    server_socket = Socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    # Опция, делающая приложение устойчивым к сбоям, связанным с привязкой к портам и облегчает перезапуск серверов без задержек или ошибок, связанных с занятостью адреса.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('127.0.0.1', 8000))
    
    # Активация прослушивания.
    server_socket.listen()

    await listen_for_connections(server_socket=server_socket, loop=loop)
    

if __name__ == '__main__':
    loop = EventLoop()

    loop.run(main=main(loop=loop))