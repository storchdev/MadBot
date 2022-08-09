from cogs import utils
from config import TOKEN
import db
import discord
from discord.ext import commands
from cogs.utils import handle_error
import time
import aiohttp
import asyncio


intents = discord.Intents.default()
COGS = (
    'cogs.listeners',
    'cogs.madlibs',
    'cogs.misc',
    'cogs.custom',
    'jishaku'
)


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True)
        )
        self.owner_ids = [718475543061987329]
        self.CannotEmbedLinks = utils.CannotEmbedLinks
        self.handle_error = handle_error

    async def setup_hook(self):
        await self.tree.sync()
        print('Synced commands')

        for cog in COGS:
            await self.load_extension(cog)
            print(f'Loaded {cog}')

        self.up_at = time.time()
        self.session = aiohttp.ClientSession()
        self.owner = await self.fetch_user(self.owner_ids[0])
        self.db = await db.connect()

        print('Ready')


bot = Bot()


async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

