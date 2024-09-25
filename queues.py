import asyncio, random


class Product:

    def __init__(self, name: str, checkout_time: float) -> None:
        self.name = name
        self.checkout_time = checkout_time


class Customer:

    def __init__(self, id, products: list[Product]) -> None:
        self.id = id
        self.products = products


async def checkout_customer(queue: asyncio.Queue, id) -> None:
    while True:
        customer: Customer = await queue.get()

        print(f'Cashier({id}) - Customer({customer.id})')
        for product in customer.products:
            print(f'Cashier({id}) checkouts Customer({customer.id}): {product.name}')
            await asyncio.sleep(delay=product.checkout_time)
            print(f'Cashier({id}) finished checkouting Customer({customer.id})')
        
        queue.task_done()

def generate_customer(id: int) -> Customer:
    products_all = [
        Product(name='Milk', checkout_time=1),
        Product(name='Coffee', checkout_time=2),
        Product(name='Sugar', checkout_time=3),
    ]

    products = [products_all[random.randrange(len(products_all))] for _ in range(random.randrange(10))]

    return Customer(id=id, products=products)

async def customer_generator(queue: asyncio.Queue) -> None:
    total_customers = 0

    while True:
        customers = [generate_customer(id=id) for id in range(total_customers, total_customers + random.randrange(10))]

        for customer in customers:
            print('Waiting for adding the customer to the queue.')
            await queue.put(customer)
            print('The customer was added to the queue.')

        total_customers + len(customers)
        await asyncio.sleep(delay=1)

async def main() -> None:
    queue = asyncio.Queue(maxsize=5)

    customer_producer = asyncio.create_task(coro=customer_generator(queue=queue))

    cashiers = [asyncio.create_task(coro=checkout_customer(queue=queue, id=id)) for id in range(3)]

    await asyncio.gather(customer_producer, *cashiers)


if __name__ == '__main__':
    asyncio.run(main=main())