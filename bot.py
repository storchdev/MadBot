from config import TOKEN
import db
import discord
from discord.ext import commands
import time
import aiohttp
import asyncio
import logging


logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
COGS = (
    'cogs.listeners',
    'cogs.madlibs',
    'cogs.misc',
    'cogs.custom',
    'jishaku'
)


class MadLibsBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True)
        )
        self.owner_ids = [718475543061987329]

    async def setup_hook(self):
        print(f'{bot.user} has connected to Discord.')
        await self.loop.create_task(self.setup_task())

    async def setup_task(self):
        await self.wait_until_ready()
        
        for cog in COGS:
            await self.load_extension(cog)
            print(f'Loaded {cog}')

        self.up_at = time.time()
        self.session = aiohttp.ClientSession()
        self.owner = await self.fetch_user(self.owner_ids[0])
        self.db = await db.connect()
        self.app_commands = await self.tree.fetch_commands()


bot = MadLibsBot()


async def inter_check(interaction):
    if not interaction.channel.permissions_for(interaction.guild.me).embed_links:
        await interaction.response.send_message(
            f':no_entry: Ensure that I have the `Embed Links` permission in this channel.',
            ephemeral=True
        )
        return False

    return True

bot.tree.interaction_check = inter_check


@commands.dm_only()
@commands.is_owner()
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.message.add_reaction('\u2705')


async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

