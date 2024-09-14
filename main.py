import asyncpg, decouple
from aiohttp.web import RouteTableDef, Request, Response, Application, HTTPNotFound, HTTPBadRequest, json_response, run_app


async def create_db_pool(app: Application) -> None:
    app['db'] = await asyncpg.create_pool(host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database='products', min_size=6, max_size=6)

async def destroy_db_pool(app: Application) -> None:
    pool: asyncpg.Pool = app['db']
    await pool.close()


routes = RouteTableDef()

@routes.get(path='/brands')
async def brands(request: Request) -> Response:
    pool: asyncpg.Pool = request.app['db']
    results: list[asyncpg.Record] = await pool.fetch(query='SELECT brand_id, brand_name FROM brand;')
    return json_response(data=[dict(brand) for brand in results])

@routes.get(path='/products/{id}')
async def get_product(request: Request) -> Response:
    try:
        pool: asyncpg.Pool = request.app['db']
        product_id = int(request.match_info['id'])
        result: asyncpg.Record = await pool.fetchrow('SELECT product_id, product_name, brand_id FROM product WHERE product_id = $1;', product_id)

        if result is not None: return json_response(data=dict(result))
        else: raise HTTPNotFound()
    except: raise HTTPBadRequest()

@routes.post(path='/product')
async def create_product(request: Request) -> Response:
    if not request.can_read_body: raise HTTPBadRequest()
    else: body = await request.json()

    if 'product_name' in body and 'brand_id' in body:
        pool: asyncpg.Pool = request.app['db']
        await pool.execute('INSERT INTO product (product_name, brand_id) VALUES ($1, $2)', body['product_name'], int(body['brand_id']))
        return Response(status=201)
    else: raise HTTPBadRequest()


if __name__ == '__main__':
    app = Application()
    app.on_startup.append(create_db_pool); app.on_cleanup.append(destroy_db_pool)
    app.add_routes(routes=routes)
    run_app(app=app)