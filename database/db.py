import aiosqlite3 
import asyncio 


loop = asyncio.get_event_loop()


async def connect():
    open('./main.db', 'a+')
    con = await aiosqlite3.connect('./main.db')
    return con

db = loop.run_until_complete(connect())


async def create_tables():
    queries = [
        '''CREATE TABLE IF NOT EXISTS prefixes (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "guild_id" INTEGER,
            "prefix" TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS madlibs (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "guild_id" INTEGER,
            "name" TEXT,
            "template" TEXT,
            "creator_id" INTEGER,
            "plays" INTEGER
        )'''
    ]

    async with db.cursor() as cur:
        for query in queries:
            await cur.execute(query)


async def get_prefixes():
    query = 'SELECT guild_id, prefix FROM prefixes'
    p = {}

    async with db.cursor() as cur:
        await cur.execute(query)

        for prefix in await cur.fetchall():
            p[prefix[0]] = p[1]

    return p


loop.run_until_complete(create_tables())
prefixes = loop.run_until_complete(get_prefixes())
