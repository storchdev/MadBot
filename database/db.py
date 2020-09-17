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

    [await db.execute(query) for query in queries]
    return db


loop.run_until_complete(create_tables())
