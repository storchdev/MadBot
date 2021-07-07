from db import db
import asyncio


def _case(prefix):
    return [
        prefix,
        prefix.upper(),
        prefix.lower(),
        prefix.capitalize()
    ]


async def _get_prefixes():
    query = 'SELECT guild_id, prefix FROM prefixes'
    return {res['guild_id']: res['prefix'] for res in await db.fetch(query)}


prefixes = asyncio.get_event_loop().run_until_complete(_get_prefixes())


def get_prefix(bot, message):
    base = [f'<@{bot.user.id}> ', f'<@!{bot.user.id}> ']
    prefix = bot.prefixes.get(message.guild.id)
    return (_case(prefix) if prefix else ['ml!', 'ML!', 'Ml!']) + base
