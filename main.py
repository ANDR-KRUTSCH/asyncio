import asyncio, asyncpg, random, decouple
from asyncpg import Connection, Pool, Record
from typing import Coroutine, Any
from util import async_timed


async def init_db(database: str) -> Connection:
    print(f'DB: {database}. Connecting...')
    connection: Connection = await asyncpg.connect(database=database, host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'))
    print(f'DB: {database}. Connected.')

    queries = {
        1: 'CREATE TABLE IF NOT EXISTS brand (brand_id serial PRIMARY KEY, brand_name text NOT NULL);',
        2: 'CREATE TABLE IF NOT EXISTS product (product_id serial PRIMARY KEY, product_name text NOT NULL, brand_id int NOT NULL, FOREIGN KEY (brand_id) REFERENCES brand(brand_id));',
        3: 'CREATE TABLE IF NOT EXISTS product_color (product_color_id serial PRIMARY KEY, product_color_name text NOT NULL);',
        4: 'CREATE TABLE IF NOT EXISTS product_size (product_size_id serial PRIMARY KEY, product_size_name text NOT NULL);',
        5: 'CREATE TABLE IF NOT EXISTS sku (sku_id serial PRIMARY KEY, product_id int NOT NULL, product_size_id int NOT NULL, product_color_id int NOT NULL, FOREIGN KEY (product_id) REFERENCES product(product_id), FOREIGN KEY (product_size_id) REFERENCES product_size(product_size_id), FOREIGN KEY (product_color_id) REFERENCES product_color(product_color_id));',
    }

    async with connection.transaction():
        keys = list(queries.keys()); keys.sort()
        for key in keys:
            result = await connection.execute(query=queries[key])
            print(f'{key}. {result}')
        try:
            async with connection.transaction():
                print(await connection.execute(query='INSERT INTO product_color VALUES (1, \'Blue\'), (2, \'Black\');'))
                print(await connection.execute(query='INSERT INTO product_size VALUES (1, \'Small\'), (2, \'Medium\'), (3, \'Large\');'))
        except: pass

    print(f'DB: {database}. Initialized.')
    return connection

async def clear_db(connection: Connection) -> None:
    for table in ['brand', 'product', 'product_color', 'product_size', 'sku']:
        print(await connection.execute(query=f'DROP TABLE {table} CASCADE;'))

async def insert_brands(connection: Connection) -> Coroutine[Any, Any, Any]:
    with open(file='common_words.txt') as file:
        words = file.readlines()
        brands = [(index, words[index].replace('\n', '')) for index in range(1, 101)]
        return await connection.executemany(command='INSERT INTO brand (brand_id, brand_name) VALUES ($1, $2);', args=brands)

async def insert_products(connection: Connection) -> Coroutine[Any, Any, Any]:
    with open(file='common_words.txt') as file:
        words = file.readlines()
        products = [(index, words[index + 100].replace('\n', ''), random.randint(1, 100)) for index in range(1, 1001)]
        return await connection.executemany(command='INSERT INTO product (product_id, product_name, brand_id) VALUES ($1, $2, $3);', args=products)
    
async def insert_skus(connection: Connection) -> Coroutine[Any, Any, Any]:
    skus = [(random.randint(1, 1000), random.randint(1, 3), random.randint(1, 2)) for _ in range(100000)]
    await connection.executemany(command='INSERT INTO sku (product_id, product_size_id, product_color_id) VALUES ($1, $2, $3);', args=skus)

async def query_products(pool: Pool):
    async with pool.acquire() as connection:
        connection: Connection
        return await connection.fetchrow(query='SELECT p.product_id, p.product_name, p.brand_id, s.sku_id, pc.product_color_name, ps.product_size_name FROM product AS p JOIN sku AS s ON s.product_id = p.product_id JOIN product_color AS pc ON pc.product_color_id = s.product_color_id JOIN product_size AS ps ON ps.product_size_id = s.product_size_id WHERE p.product_id = 100;')
    
@async_timed()
async def query_products_sync(pool: Pool, queries):
    return [await query_products(pool=pool) for _ in range(queries)]

@async_timed()
async def query_products_async(pool: Pool, queries):
    queries = [query_products(pool=pool) for _ in range(queries)]
    return await asyncio.gather(*queries)

async def main() -> None:
    connection = await init_db(database='products')

    try:
        async with connection.transaction():
            print(await insert_brands(connection=connection))
            print(await insert_products(connection=connection))
            print(await insert_skus(connection=connection))

            # print(await connection.fetch(query='SELECT p.product_id, p.product_name, p.brand_id, s.sku_id, pc.product_color_name, ps.product_size_name FROM product AS p JOIN sku AS s ON s.product_id = p.product_id JOIN product_color AS pc ON pc.product_color_id = s.product_color_id JOIN product_size AS ps ON ps.product_size_id = s.product_size_id WHERE p.product_id = 100;'))

            async for _ in connection.cursor(query='SELECT * FROM product;'):
                print(_)
    except: await clear_db(connection=connection)
    finally: await connection.close()

async def main_loop() -> None:
    async with asyncpg.create_pool(database='products', host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), min_size=6, max_size=6) as pool:
        # await asyncio.gather(query_products(pool=pool), query_products(pool=pool))
        await query_products_sync(pool=pool, queries=10000)
        await query_products_async(pool=pool, queries=10000)


if __name__ == '__main__':
    asyncio.run(main=main())