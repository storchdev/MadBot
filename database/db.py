import aiosqlite3 
import asyncio 


loop = asyncio.get_event_loop()


async def connect():
    con = await aiosqlite3.connect('./main.db')
    return con

db = loop.run_until_complete(connect())


async def create_tables():
    queries = [
        '''CREATE TABLE IF NOT EXISTS prefixes (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "guild_id" INTEGER,
            "prefix" TEXT
        )'''
    ]

    async with db.cursor() as cur:
        for query in queries:
            await cur.execute(query)


async def get_prefixes():
    query = 'SELECT guild_id, prefix FROM prefixes'
    prefixes = {}

    async with db.cursor() as cur:
        await cur.execute(query)

        for prefix in await cur.fetchall():
            prefixes[prefix[0]] = prefixes[1]

    return prefixes 


loop.run_until_complete(create_tables())
prefixes = loop.run_until_complete(get_prefixes())
    