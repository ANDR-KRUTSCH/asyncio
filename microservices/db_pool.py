import asyncpg
from aiohttp.web import Application


async def create_db_pool(app: Application, host: str, port: int, user: str, password: str, database: str) -> None:
    app['db'] = await asyncpg.create_pool(host=host, port=port, user=user, password=password, database=database, min_size=6, max_size=6)

async def destroy_db_pool(app: Application) -> None:
    pool: asyncpg.Pool = app['db']
    await pool.close()