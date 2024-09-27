import typing


class CustomFuture:

    def __init__(self) -> None:
        self._result: typing.Any = None
        self._is_finished: bool = False
        self._done_callback: typing.Callable[[typing.Any], typing.Any] = None

    def result(self) -> typing.Any:
        return self._result
    
    def is_finished(self) -> bool:
        return self._is_finished
    
    def set_result(self, result: typing.Any) -> None:
        self._result = result
        self._is_finished = True
        if self._done_callback: self._done_callback(result)

    def set_done_callback(self, callback: typing.Callable[[typing.Any], typing.Any]) -> None:
        self._done_callback = callback

    def __await__(self):
        if self.is_finished(): return self.result()
        else: yield self


if __name__ == '__main__':
    future = CustomFuture()

    try:
        for _ in range(1, 6):
            print('Checking for the result of the future object.')
            gen = future.__await__()
            gen.send(None)
            print('The future object does not have the result yet.')
            if _ == 3:
                print('Setting the result of the future object.')
                future.set_result(result='result')
    except StopIteration as stop_iteration:
        print('The future object result:', stop_iteration.value)