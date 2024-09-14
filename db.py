import asyncio, asyncpg, decouple, random
from typing import Coroutine, Any


async def init_db(database: str) -> asyncpg.Connection:
    print(f'DB: {database}. Connecting...')
    connection: asyncpg.Connection = await asyncpg.connect(host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database=database)
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

async def clear_db(connection: asyncpg.Connection) -> None:
    for table in ['brand', 'product', 'product_color', 'product_size', 'sku']:
        print(await connection.execute(query=f'DROP TABLE {table} CASCADE;'))

async def insert_brands(connection: asyncpg.Connection) -> Coroutine[Any, Any, Any]:
    with open(file='common_words.txt') as file:
        words = file.readlines()
        brands = [(index, words[index].replace('\n', '')) for index in range(1, 101)]
        return await connection.executemany(command='INSERT INTO brand (brand_id, brand_name) VALUES ($1, $2);', args=brands)

async def insert_products(connection: asyncpg.Connection) -> Coroutine[Any, Any, Any]:
    with open(file='common_words.txt') as file:
        words = file.readlines()
        products = [(index, words[index + 100].replace('\n', ''), random.randint(1, 100)) for index in range(1, 1001)]
        return await connection.executemany(command='INSERT INTO product (product_id, product_name, brand_id) VALUES ($1, $2, $3);', args=products)

async def insert_skus(connection: asyncpg.Connection) -> Coroutine[Any, Any, Any]:
    skus = [(random.randint(1, 1000), random.randint(1, 3), random.randint(1, 2)) for _ in range(100000)]
    await connection.executemany(command='INSERT INTO sku (product_id, product_size_id, product_color_id) VALUES ($1, $2, $3);', args=skus)

async def main() -> None:
    connection = await init_db(database='products')

    try:
        async with connection.transaction():
            print(await insert_brands(connection=connection))
            print(await insert_products(connection=connection))
            print(await insert_skus(connection=connection))
            
            async for _ in connection.cursor(query='SELECT * FROM product;'):
                print(_)
    except: await clear_db(connection=connection)
    finally: await connection.close()


if __name__ == '__main__':
    asyncio.run(main=main())