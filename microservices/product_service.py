import asyncpg, functools, decouple
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app, json_response
from db_pool import create_db_pool, destroy_db_pool


routes = RouteTableDef()

@routes.get(path='/products')
async def products(request: Request) -> Response:
    pool: asyncpg.Pool = request.app['db']
    result: list[asyncpg.Record] = await pool.fetch(query='SELECT product_id, product_name FROM product LIMIT 5;')
    return json_response(data=[dict(product) for product in result])


app = Application()
app.on_startup.append(functools.partial(create_db_pool, host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database='products'))
app.on_cleanup.append(destroy_db_pool)
app.add_routes(routes=routes)
run_app(app=app, host='127.0.0.1', port=8000)