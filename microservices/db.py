import asyncio, asyncpg, decouple


async def init_cart_db(database: str) -> asyncpg.Connection:
    print(f'DB: {database}. Connecting...')
    connection: asyncpg.Connection = await asyncpg.connect(host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database=database)
    print(f'DB: {database}. Connected.')

    queries = {
        1: 'CREATE TABLE IF NOT EXISTS user_cart (user_id int NOT NULL, product_id int NOT NULL);',
    }

    async with connection.transaction():
        keys = list(queries.keys()); keys.sort()
        for key in keys:
            result = await connection.execute(query=queries[key])
            print(f'{key}. {result}')
        try:
            async with connection.transaction():
                print(await connection.execute(query='INSERT INTO user_cart VALUES (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 5);'))
        except: pass

    print(f'DB: {database}. Initialized.')
    return connection

async def init_favorite_db(database: str) -> asyncpg.Connection:
    print(f'DB: {database}. Connecting...')
    connection: asyncpg.Connection = await asyncpg.connect(host='127.0.0.1', port=5432, user='postgres', password=decouple.config('DB_PASSWORD'), database=database)
    print(f'DB: {database}. Connected.')

    queries = {
        1: 'CREATE TABLE IF NOT EXISTS user_favorite (user_id int NOT NULL, product_id int NOT NULL);',
    }

    async with connection.transaction():
        keys = list(queries.keys()); keys.sort()
        for key in keys:
            result = await connection.execute(query=queries[key])
            print(f'{key}. {result}')
        try:
            async with connection.transaction():
                print(await connection.execute(query='INSERT INTO user_favorite VALUES (1, 1), (1, 2), (1, 3), (3, 1), (3, 2), (3, 5);'))
        except: pass

    print(f'DB: {database}. Initialized.')
    return connection

async def clear_cart_db(connection: asyncpg.Connection) -> None:
    print(await connection.execute(query=f'DROP TABLE user_cart;'))

async def clear_favorite_db(connection: asyncpg.Connection) -> None:
    print(await connection.execute(query=f'DROP TABLE user_favorite;'))

async def main() -> None:
    cart = await init_cart_db(database='cart')
    favorite = await init_favorite_db(database='favorites')
    
    await cart.close()
    await favorite.close()


if __name__ == '__main__':
    asyncio.run(main=main())