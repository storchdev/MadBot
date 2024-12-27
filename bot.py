from typing import Any

from discord.client import Client
from discord.interactions import Interaction
from config import TOKEN
import db
import discord
from discord.ext import commands
import time
import aiohttp
import asyncio
from discord import app_commands 


discord.utils.setup_logging()

intents = discord.Intents.default()
COGS = (
    'cogs.listeners',
    'cogs.madlibs',
    'cogs.misc',
    'cogs.custom',
    'jishaku',
    'cogs.admin',
    'cogs.topgg'
)

class Tree(app_commands.CommandTree):
    def __init__(self, client: Client, *, fallback_to_global: bool = True):
        super().__init__(client, fallback_to_global=fallback_to_global)
    
    async def interaction_check(self, interaction):
        if not interaction.channel.permissions_for(interaction.guild.me).embed_links:
            await interaction.response.send_message(
                f':no_entry: Ensure that I have the `Embed Links` permission in this channel.',
                ephemeral=True
            )
            return False
        return True


class MadBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
            tree_cls=Tree
        )
        self.owner_ids = [718475543061987329]

    async def setup_hook(self):
        print(f'{bot.user} has connected to Discord.')
        self.loop.create_task(self.setup_task())

    async def setup_task(self):
        await self.wait_until_ready()
        
        self.up_at = time.time()
        self.session = aiohttp.ClientSession()
        self.owner = await self.fetch_user(self.owner_ids[0])
        self.db = await db.connect()
        self.app_commands = await self.tree.fetch_commands()

        for cog in COGS:
            await self.load_extension(cog)
            print(f'Loaded {cog}')

        self.incognito = set(row['user_id'] for row in await self.db.fetch('SELECT user_id FROM user_settings'))


bot = MadBot()


@commands.dm_only()
@commands.is_owner()
@bot.command()
async def sync(ctx):
    for cmd in bot.tree.get_commands():
        cmd.guild_only = True 
    await bot.tree.sync()
    await ctx.message.add_reaction('\u2705')


async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

