import asyncpg, decouple, starlette
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route


async def create_db_pool() -> None:
    pool: asyncpg.Pool = await asyncpg.create_pool(host='127.0.0.1', port=5432, database='products', user='postgres', password=decouple.config('DB_PASSWORD'), min_size=6, max_size=6)
    app.state.DB = pool

async def destroy_db_pool() -> None:
    pool: asyncpg.Pool = app.state.DB
    await pool.close()


async def brands(request: Request) -> Response:
    pool: asyncpg.Pool = request.app.state.DB
    results: list[asyncpg.Record] = await pool.fetch(query='SELECT brand_id, brand_name FROM brand;')
    return JSONResponse(content=[dict(brand) for brand in results])



app = Starlette(routes=[Route(path='/brands', endpoint=brands)], on_startup=[create_db_pool], on_shutdown=[destroy_db_pool])