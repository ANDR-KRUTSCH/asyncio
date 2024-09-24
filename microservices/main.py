import aiohttp, asyncio, logging, functools
from aiohttp.web import Application, RouteTableDef, Request, Response, run_app, json_response
from datetime import datetime, timedelta
from typing import Awaitable, Coroutine, Any


class TooManyRetries(BaseException): pass


class Interrupter:

    class InterrupterResetIntervalTimeError(BaseException): pass
    class InterrupterAttemptIntervalTimeError(BaseException): pass

    def __init__(self,
                 coroutine: Coroutine,
                 max_failure_attempts_number: int,
                 timeout: float,
                 attempt_interval_time: float,
                 reset_interval_time: float,
                 ) -> None:
        
        self.coroutine: Coroutine = coroutine
        self.max_failure_attempts_number: int = max_failure_attempts_number
        self.timeout: float = timeout
        self.attempt_interval_time: float = attempt_interval_time
        self.reset_interval_time: float = reset_interval_time
        self.last_attempt_time: datetime = None
        self.last_failure_attempt_time: datetime = None
        self.failure_attempts_number: int = 0

    async def request(self, *args, **kwargs) -> Any:
        if self.failure_attempts_number < self.max_failure_attempts_number:
            if self.last_attempt_time is None:
                return await self._request(*args, **kwargs)
            else:
                if datetime.now() > self.last_attempt_time + timedelta(seconds=self.attempt_interval_time):
                    return await self._request(*args, **kwargs)
                else:
                    raise Interrupter.InterrupterAttemptIntervalTimeError()
        else:
            if datetime.now() > self.last_attempt_time + timedelta(seconds=self.reset_interval_time):
                self._reset()
                return await self._request(*args, **kwargs)
            else:
                raise Interrupter.InterrupterResetIntervalTimeError()
        
    def _reset(self) -> None:
        self.last_failure_attempt_time, self.failure_attempts_number = None, 0

    async def _request(self, *args, **kwargs) -> Any:
        try:
            self.last_attempt_time = datetime.now()
            return await asyncio.wait_for(fut=self.coroutine(*args, **kwargs), timeout=self.timeout)
        except BaseException as exception:
            self.last_failure_attempt_time = datetime.now()
            self.failure_attempts_number += 1
            raise exception


async def retry(coroutine: Coroutine, max_retries_number: int, timeout: float, retry_interval_time: float):
    for retry_number in range(0, max_retries_number):
        try:
            return await asyncio.wait_for(fut=coroutine(), timeout=timeout)
        except BaseException as error:
            logging.exception(msg=f'#{retry_number}. Exception was raised.', exc_info=error)
            await asyncio.sleep(delay=retry_interval_time)
    raise TooManyRetries()

routes = RouteTableDef()

@routes.get(path='/products/all')
async def all_products(request: Request) -> Response:
    requests: list[asyncio.Task] = list()
    
    async with aiohttp.ClientSession() as session:
        products_request = functools.partial(session.get, 'http://localhost:8000/products')
        favorites_request = functools.partial(session.get, 'http://localhost:8002/users/3/favorites')
        cart_request = functools.partial(session.get, 'http://localhost:8003/users/3/cart')
        
        requests.append(products := asyncio.create_task(coro=retry(coroutine=products_request,
                                                                   max_retries_number=3,
                                                                   timeout=0.1,
                                                                   retry_interval_time=0.1)))
        
        requests.append(favorites := asyncio.create_task(coro=retry(coroutine=favorites_request,
                                                                    max_retries_number=3,
                                                                    timeout=0.1,
                                                                    retry_interval_time=0.1)))
        
        requests.append(cart := asyncio.create_task(coro=retry(coroutine=cart_request,
                                                               max_retries_number=3,
                                                               timeout=0.1,
                                                               retry_interval_time=0.1)))

        done, pending = await asyncio.wait(fs=requests, timeout=1.0)

        if products in pending:
            [request.cancel() for request in requests]
            return json_response(data=dict(error='Error connecting to the products-service.'), status=504)
        elif products in done and products.exception() is not None:
            [request.cancel() for request in requests]
            logging.exception(msg='Server error when connecting to the products-service.', exc_info=products.exception())
            return json_response(data=dict(error='Error connecting to the products-service.'), status=500)
        else:
            product_response: dict = await products.result().json()

            product_results: list[dict] = await get_products_with_inventory(session=session, product_response=product_response)
            
            cart_item_count = await get_response_item_count(task=cart,
                                                            done=done,
                                                            pending=pending,
                                                            error_msg='Error getting user cart.')
            
            favorite_item_count = await get_response_item_count(task=favorites,
                                                                done=done,
                                                                pending=pending,
                                                                error_msg='Error getting user favorites.')
            
            return json_response(data=dict(cart_items=cart_item_count,
                                           favorite_items=favorite_item_count,
                                           products=product_results))

async def get_products_with_inventory(session: aiohttp.ClientSession, product_response: dict) -> list[dict]:
    async def get_inventory(session: aiohttp.ClientSession, product_id: str) -> aiohttp.ClientResponse:
        return await session.get(url=f'http://localhost:8001/products/{product_id}/inventory')
    
    def create_product_record(product_id: int, inventory: int | None = None) -> dict:
        return dict(product_id=product_id, inventory=inventory)
    
    interrupter = Interrupter(coroutine=get_inventory, max_failure_attempts_number=10, timeout=0.5, attempt_interval_time=0.000001, reset_interval_time=30.0)

    inventory_tasks_to_pid = {asyncio.create_task(coro=interrupter.request(session=session, product_id=product['product_id'])): product['product_id'] for product in product_response}

    done, pending = await asyncio.wait(fs=inventory_tasks_to_pid.keys(), timeout=1.0)

    product_results = list()

    for task in done:
        if task.exception() is None:
            product_id = inventory_tasks_to_pid[task]
            inventory = await task.result().json()
            product_results.append(create_product_record(product_id=product_id, inventory=inventory['inventory']))
        else:
            product_id = inventory_tasks_to_pid[task]
            product_results.append(create_product_record(product_id=product_id))
            logging.exception(msg=f'Error getting the information about the product\'s inventory with id={product_id}.', exc_info=task.exception())

    for task in pending:
        task.cancel()
        product_id = inventory_tasks_to_pid[task]
        product_results.append(create_product_record(product_id=product_id))

    return product_results

async def get_response_item_count(task: asyncio.Task,
                                  done: set[Awaitable],
                                  pending: set[Awaitable],
                                  error_msg: str) -> int | None:
    
    if task in done and task.exception() is None:
        return len(await task.result().json())
    elif task in pending:
        task.cancel()
    else:
        logging.exception(msg=error_msg, exc_info=task.exception())


app = Application()
app.add_routes(routes=routes)
run_app(app=app, host='127.0.0.1', port=9000)