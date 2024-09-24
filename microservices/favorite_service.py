import asyncpg, functools, decouple
from aiohttp.web import Application, RouteTableDef, Request, Response, HTTPNotFound, HTTPBadRequest, run_app, json_response
from db_pool import create_db_pool, destroy_db_pool


routes = RouteTableDef()

@routes.get(path='/users/{id}/favorites')
async def favorites(request: Request) -> Response:
    try:
        user_id = int(request.match_info['id'])
        pool: asyncpg.Pool = request.app['db']
        result: list[asyncpg.Record] = await pool.fetch(query=f'SELECT product_id FROM user_favorite WHERE user_id = {user_id}')
        if result is not None: return json_response(data=[dict(product) for product in result])
        else: raise HTTPNotFound()
    except: HTTPBadRequest()


app = Application()
app.on_startup.append(functools.partial(create_db_pool, host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database='favorites'))
app.on_cleanup.append(destroy_db_pool)
app.add_routes(routes=routes)
run_app(app=app, host='127.0.0.1', port=8002)