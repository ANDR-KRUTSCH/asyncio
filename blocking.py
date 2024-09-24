import asyncio


class MockSocket:

    def __init__(self) -> None:
        self.is_closed: bool = False

    async def send(self, message: str) -> None:
        if self.is_closed: raise Exception('Socket is closed!')
        else:
            print(f'Sending the message: "{message}".')
            await asyncio.sleep(delay=1)
            print(f'The message was sent: "{message}".')

    def close(self) -> None:
        self.is_closed = True


users = {'James': MockSocket(), 'Mary': MockSocket(), 'Maria': MockSocket()}

async def disconnect_user(username: str, user_lock: asyncio.Lock) -> None:
    async with user_lock:
        print(f'Disconnecting of user with username: "{username}"...')
        socket: MockSocket = users.pop(username)
        socket.close()
    print(f'User with username: "{username}" was disconneted!')

async def message_all_users(user_lock: asyncio.Lock) -> None:
    print('Creating of the tasks for sending the messages to all users.')
    async with user_lock:
        messages = [socket.send(message=f'Hello, {username}') for username, socket in users.items()]
        await asyncio.gather(*messages)


async def main() -> None:
    user_lock = asyncio.Lock()
    await asyncio.gather(message_all_users(user_lock=user_lock), disconnect_user(username='Maria', user_lock=user_lock))


if __name__ == '__main__':
    asyncio.run(main=main())