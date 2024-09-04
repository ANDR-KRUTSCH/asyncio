import asyncio
from aiohttp import ClientSession
from .async_timer import async_timed

@async_timed()
async def fetch_status(session: ClientSession, url: str, delay: int = 0) -> int:
    await asyncio.sleep(delay=delay)
    async with session.get(url=url) as response:
        return response.status