import asyncio
from enum import Enum   


class ConnectionState(Enum):
    WAIT_INIT = 0
    INITIALIZING = 1
    INITIALIZED = 2


class Connection:

    def __init__(self) -> None:
        self._state = ConnectionState.WAIT_INIT
        self._condition = asyncio.Condition()

    async def initialize(self) -> None:
        await self._change_state(state=ConnectionState.INITIALIZING)
        print('initialize: initializing of the connection...')
        await asyncio.sleep(delay=3)
        print('initialize: the connection was initialized.')
        await self._change_state(state=ConnectionState.INITIALIZED)

    async def execute(self, query: str) -> None:
        async with self._condition:
            print('execute: waiting for the connection\'s initialization...')
            await self._condition.wait_for(predicate=self._is_initialized)
            print(f'execute: executing "{query}"')
            await asyncio.sleep(delay=3)

    def _is_initialized(self) -> bool:
        if self._state is not ConnectionState.INITIALIZED:
            print(f'_is_initilized: the initializing of the connection is not done. State: {self._state}')
            return False
        else:
            print(f'_is_initilized: the initializing of the connection is done.')
            return True

    async def _change_state(self, state: ConnectionState) -> None:
        async with self._condition:
            print(f'change_state: from {self._state} to {state}')
            self._state = state
            self._condition.notify_all()


async def main() -> None:
    connection = Connection()
    query_1 = asyncio.create_task(coro=connection.execute(query='SELECT * FROM table;'))
    query_2 = asyncio.create_task(coro=connection.execute(query='SELECT * FROM another_table;'))

    asyncio.create_task(coro=connection.initialize())
    
    await query_1
    await query_2


if __name__ == '__main__':
    asyncio.run(main=main())