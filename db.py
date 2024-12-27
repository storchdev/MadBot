from config import POSTGRES_CONFIG
import asyncpg


async def connect():
    con = await asyncpg.create_pool(**POSTGRES_CONFIG)
    await _create_tables(con)
    return con


async def _create_tables(con):
    queries = [
        '''CREATE TABLE IF NOT EXISTS plays (
            "id" SERIAL PRIMARY KEY,
            "channel_id" BIGINT,
            "participants" JSON,
            "final_story" TEXT,
            "played_at" INTEGER,
            "name" VARCHAR(32),
            "guild_id" BIGINT
        )''',
        '''CREATE TABLE IF NOT EXISTS madlibs (
            "id" SERIAL PRIMARY KEY,
            "guild_id" BIGINT,
            "name" VARCHAR(32),
            "template" TEXT,
            "creator_id" BIGINT,
            "plays" BIGINT,
            "created_at" INTEGER
        )''',
        '''CREATE TABLE IF NOT EXISTS settings (
            "id" SERIAL PRIMARY KEY,
            "guild_id" BIGINT UNIQUE,
            "time_limit" INTEGER DEFAULT 45,
            "max_players" INTEGER DEFAULT 10,
            "max_games" INTEGER DEFAULT 1,
            "show_entered" BOOLEAN DEFAULT TRUE
        )''',
        '''CREATE TABLE IF NOT EXISTS user_settings (
            "id" SERIAL PRIMARY KEY,
            "user_id" BIGINT UNIQUE,
            "incognito" BOOLEAN
        )'''
    ]

    [await con.execute(query) for query in queries]
