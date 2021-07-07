from cogs.prefix import get_prefix, prefixes
from cogs import utils
from discord.ext import commands
from config import TOKEN
from db import db
import discord
import re


intents = discord.Intents.default()
COGS = (
    'cogs.help',
    'cogs.listeners',
    'cogs.blacklist',
    'cogs.madlibs',
    'cogs.config',
    'cogs.speech',
    'cogs.misc',
    'cogs.topgg',
    'jishaku'
)
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    activity=discord.Game('ml!help'),
    help_command=None,
    intents=intents
)
bot.db = db
bot.prefixes = prefixes
bot.finder = re.compile('{(.+?)}')
bot.Blacklisted = utils.Blacklisted
bot.CannotEmbedLinks = utils.CannotEmbedLinks
bot.blacklisted = []

[bot.load_extension(cog) for cog in COGS]


@bot.event
async def on_message(message):
    if not message.guild or message.author.bot or message.author.id in bot.blacklisted:
        return
    if message.content in (f'<@{bot.user.id}>', f'<@!{bot.user.id}>'):
        try:
            msg = f':wave: Hello, a bot here. Do `{get_prefix(bot, message)[0]}help` to see my commands.'
            await message.channel.send(msg)
        except discord.Forbidden:
            pass
    await bot.process_commands(message)


if __name__ == '__main__':
    bot.run(TOKEN)
