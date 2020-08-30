from config import POSTGRES_CONFIG
import asyncio
import asyncpg


loop = asyncio.get_event_loop()


async def connect():
    con = await asyncpg.create_pool(**POSTGRES_CONFIG)
    return con

db = loop.run_until_complete(connect())


async def create_tables():
    queries = [
        '''CREATE TABLE IF NOT EXISTS prefixes (
            "id" SERIAL,
            "guild_id" BIGINT,
            "prefix" VARCHAR(16)
        )''',
        '''CREATE TABLE IF NOT EXISTS plays (
            "id" SERIAL,
            "channel_id" BIGINT,
            "participants" JSON,
            "final_story" TEXT,
            "played_at" INTEGER,
            "name" VARCHAR(32),
            "guild_id" BIGINT
        )''',
        '''CREATE TABLE IF NOT EXISTS madlibs (
            "id" SERIAL,
            "guild_id" BIGINT,
            "name" VARCHAR(32),
            "template" TEXT,
            "creator_id" BIGINT,
            "plays" BIGINT,
            "created_at" INTEGER
        )''',
        '''CREATE TABLE IF NOT EXISTS messages (
            "id" SERIAL,
            "message_id" BIGINT,
            "author_id" BIGINT,
            "channel_id" BIGINT,
            "guild_id" BIGINT,
            "content" TEXT,
            "timestamp" INTEGER,
            "is_bot" BOOLEAN,
            "attachments" JSON,
            "embeds" JSON,
            "is_edited" BOOLEAN,
            "is_deleted" BOOLEAN
        )''',
        '''CREATE TABLE IF NOT EXISTS member_logs (
            "id" SERIAL,
            "member_id" BIGINT,
            "nickname" VARCHAR(32),
            "roles" JSON
        )''',
        '''CREATE TABLE IF NOT EXISTS user_logs (
            "id" SERIAL,
            "user_id" BIGINT,
            "avatar_url" TEXT,
            "username" VARCHAR(64)
        )'''
    ]

    async with db.acquire() as cur:
        for query in queries:
            await cur.execute(query)


async def get_prefixes():
    query = 'SELECT guild_id, prefix FROM prefixes'
    p = {}

    async with db.acquire() as cur:
        for prefix in await cur.fetch(query):
            p[prefix[0]] = prefix[1]

    return p


async def fetchall(query, params: tuple):
    if not params:
        async with db.acquire() as con:
            rows = await con.fetch(query)
    else:
        async with db.acquire() as con:
            rows = await con.fetch(query, *params)
    return rows


async def fetchone(query, params: tuple):
    if not params:
        async with db.acquire() as con:
            row = await con.fetchrow(query)
    else:
        async with db.acquire() as con:
            row = await con.fetchrow(query, *params)
    return row


async def execute(query, params: tuple):
    if not params:
        async with db.acquire() as con:
            await con.execute(query)
    else:
        async with db.acquire() as con:
            await con.execute(query, *params)


loop.run_until_complete(create_tables())
prefixes = loop.run_until_complete(get_prefixes())
