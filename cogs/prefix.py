from db import db


def case(prefix):
    return [
        prefix,
        prefix.upper(),
        prefix.lower(),
        prefix.capitalize()
    ]


async def get_prefixes():
    query = 'SELECT guild_id, prefix FROM prefixes'
    return {res['guild_id']: res['prefix'] for res in await db.fetch(query)}


prefixes = asyncio.get_event_loop().run_until_complete(get_prefixes())


def get_prefix(client, message):
    prefix = prefixes.get(message.guild.id)
    return case(prefix) if prefix else ['ml!', 'ML!', 'Ml!']
   
