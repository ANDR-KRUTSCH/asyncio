import asyncio, random


class Product:

    def __init__(self, name: str, checkout_time: float) -> None:
        self.name = name
        self.checkout_time = checkout_time


class Customer:

    def __init__(self, id, products: list[Product]) -> None:
        self.id = id
        self.products = products


async def checkout_customer(queue: asyncio.Queue, id: int) -> None:
    while not queue.empty():
        customer: Customer = queue.get_nowait()
        print(f'cashier({id}) - customer({customer.id})')

        for product in customer.products:
            print(f'cashier({id}) - customer({customer.id}): {product.name}')
            await asyncio.sleep(delay=product.checkout_time)
        
        print(f'cashier({id}) - customer({customer.id}):\t\t\tDone')
        queue.task_done()


async def main() -> None:
    queue = asyncio.Queue()

    products_all = [
        Product(name='Bread', checkout_time=0.1),
        Product(name='Butter', checkout_time=0.2),
        Product(name='Milk', checkout_time=0.3),
        Product(name='Coffee', checkout_time=0.4),
    ]

    for customer_id in range(10):
        products = [products_all[random.randrange(len(products_all))] for _ in range(random.randrange(10))]
        queue.put_nowait(Customer(id=customer_id, products=products))
    
    cashiers = [asyncio.create_task(coro=checkout_customer(queue=queue, id=cashier_id)) for cashier_id in range(3)]

    await asyncio.gather(queue.join(), *cashiers)


if __name__ == '__main__':
    asyncio.run(main=main())