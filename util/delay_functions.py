import asyncio

async def delay(delay_seconds: int) -> int:
    print(f'Starting waiting for {delay_seconds} second(s).')
    await asyncio.sleep(delay=delay_seconds)
    print(f'Waiting for {delay_seconds} second(s) finished.')
    return delay_seconds