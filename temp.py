from threading import RLock


class IntListThreadsafe:

    def __init__(self, wrapped_list: list[int]) -> None:
        self._lock = RLock()
        self._inner_list = wrapped_list

    def indeces_of(self, to_find: int) -> list[int]:
        with self._lock:
            enumerator = enumerate(self._inner_list)
            return [index for index, value in enumerator if value == to_find]
        
    def find_and_replace(self, to_replace: int, replace_with: int) -> None:
        with self._lock:
            indices = self.indeces_of(to_find=to_replace)
            for index in indices:
                self._inner_list[index] = replace_with


threadsafe_list = IntListThreadsafe(wrapped_list=[1, 2, 1, 2, 1])
threadsafe_list.find_and_replace(to_replace=1, replace_with=2)

print(threadsafe_list._inner_list)