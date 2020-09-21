from config import POSTGRES_CONFIG
import asyncio
import asyncpg


loop = asyncio.get_event_loop()


async def _connect():
    con = await asyncpg.create_pool(**POSTGRES_CONFIG)
    return con

db = loop.run_until_complete(_connect())


async def create_tables():
    queries = [
        '''CREATE TABLE IF NOT EXISTS prefixes (
            "id" SERIAL,
            "guild_id" BIGINT UNIQUE,
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
        )'''
    ]

    [await db.execute(query) for query in queries]
    return db


loop.run_until_complete(create_tables())
