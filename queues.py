import asyncio, random
from aiohttp.web import Application, run_app, RouteTableDef, Request, Response


routes = RouteTableDef()


@routes.get(path='/order')
async def place_order(request: Request) -> Response:
    queue_order: asyncio.Queue = request.app['queue_order']
    await queue_order.put(item=random.randrange(5))
    return Response(body='Order placed!')


async def order_processer(processer_id: int, queue: asyncio.Queue) -> None:
    while True:
        print(f'Processer({processer_id}): waiting for the order...')
        order: int = await queue.get()
        print(f'Processer({processer_id}): processing the Order({order})...')
        await asyncio.sleep(delay=order)
        print(f'Processer({processer_id}): processed the Order({order}).')
        queue.task_done()

async def create_queue_order(app: Application) -> None:
    print('Creating of the order-queue and tasks...')
    queue_order = asyncio.Queue(maxsize=10)
    app['queue_order'] = queue_order
    app['order_tasks'] = [asyncio.create_task(coro=order_processer(processer_id=id, queue=queue_order)) for id in range(5)]

async def destroy_queue_order(app: Application) -> None:
    order_tasks: list[asyncio.Task] = app['order_tasks']
    queue_order: asyncio.Queue = app['queue_order']
    print('Waiting for the processers in the async queue...')
    try:
        await asyncio.wait_for(queue_order.join(), timeout=10)
    finally:
        print('All orders processed. Canceling of tasks...')
        [task.cancel() for task in order_tasks]


if __name__ == '__main__':
    app = Application()

    app.add_routes(routes=routes)

    app.on_startup.append(create_queue_order)
    app.on_cleanup.append(destroy_queue_order)

    run_app(app=app)