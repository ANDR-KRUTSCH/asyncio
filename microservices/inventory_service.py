import random, asyncio
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app, json_response


routes = RouteTableDef()

@routes.get(path='/products/{id}/inventory')
async def get_inventory(request: Request) -> Response:
    # await asyncio.sleep(delay=random.randint(0, 5))
    return json_response(data=dict(inventory=random.randint(0, 100)))


app = Application()
app.add_routes(routes=routes)
run_app(app=app, host='127.0.0.1', port=8001)