from cogs.prefix import get_prefix, prefixes
from discord.ext import commands
from config import TOKEN
from db import db
import discord
import asyncio
import json
import re
import time


cogs = (
    'cogs.listeners',
    'cogs.blacklist',
    'cogs.madlibs',
    'cogs.config',
    'cogs.speech',
    'jishaku'
)
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    activity=discord.Game('ml!help')
)
bot.remove_command('help')
bot.db = db
bot.prefixes = prefixes
bot.finder = re.compile('{(.+?)}')

with open('./cogs/json/defaults.json') as f:
    bot.lengths = {}
    bot.defaults = json.load(f)
    bot.templates = {}
    bot.names = {}
    count = 1

    for default in bot.defaults:
        length = len(bot.finder.findall(bot.defaults[default]))
        bot.lengths[default] = length
        bot.templates[count] = bot.defaults[default]
        bot.names[count] = default
        count += 1

[bot.load_extension(cog) for cog in cogs]

ICON = 'https://media.discordapp.net/attachments/742973400636588056/745710912257916950/159607234227809532.png'
INVITE = 'https://discord.com/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot'
GITHUB = 'https://github.com/Stormtorch002/MadLibs'


@bot.event
async def on_message(message):
    if not message.guild or message.author.bot:
        return
    if message.content in (f'<@{bot.user.id}>', f'<@!{bot.user.id}>'):
        try:
            msg = f'Hello, a bot here. Do `{get_prefix(bot, message)[0]}help` to see my commands.'
            return await message.channel.send(msg)
        except discord.Forbidden:
            return
    await bot.process_commands(message)


@bot.command()
@commands.cooldown(2, 60, commands.BucketType.user)
async def feedback(ctx, *, user_feedback):
    embed = discord.Embed(
        title='New Feedback!',
        description=f'`{user_feedback}`',
        color=ctx.author.color
    )
    embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url_as(format='png')))
    embed.set_footer(text=f'Guild ID: {ctx.guild.id}')
    await bot.get_user(553058885418876928).send(embed=embed)
    await ctx.send(':thumbsup: Your feedback has been sent!')


@feedback.error
async def feedback_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You can only give feedback twice per hour. Please wait another '
                       f'`{error.retry_after:.2f}` seconds.')


@bot.command()
async def invite(ctx):
    await ctx.send(f'**You can invite me here:**\n'
                   f'<https://discord.com/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot>')


@bot.command()
async def ping(ctx):
    websocket = round(bot.latency * 1000, 2)
    t1 = time.perf_counter()
    message = await ctx.send('Pinging...')
    t2 = time.perf_counter()
    api = round((t2 - t1) * 1000, 2)
    await message.edit(content=f'**Websocket:** `{websocket}ms`\n**API:** `{api}ms`')


@bot.command(name='help', aliases=['cmds', 'commands'])
async def _help(ctx):
    if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
        return await ctx.send('I need the `Embed Links` permission to display help.')

    embed = discord.Embed(
        title='MadLibs Commands List',
        description='Hello! I am a bot made by **Stormtorch#8984**! '
                    'Commands are listed below with brief descriptons. '
                    'They may not contain every single command.',
        color=discord.Colour.blue()
    )
    embed.set_thumbnail(url=ICON)
    p = ctx.prefix.lower()

    cmds = {
        f"\U0001f4ac | {p}**prefix**": 'Shows/changes the current server prefix',
        f"\U0001f517 | {p}**invite**": 'Sends my invite link!',
        f"\U0001f9e9 | {p}**madlibs**": 'Lets you host a MadLibs game',
        f"\U0001f602 | {p}**plays**": "Gets a play from the history of the server's laughable moments",
        f"\U0001f60e | {p}**custom**": 'Manages custom story templates',
        f"\U0001f4dd | {p}**feedback**": "Gives feedback about anything related to the bot",
        f"\U0001f524 | {p}**pos**": "An aid to show info on the parts of speech",
        f"\U0001f3d3 | {p}**ping**": "ponggers"
    }

    [embed.add_field(name=cmd, value=cmds[cmd]) for cmd in cmds]
    embed.add_field(
        name='\U0001f447 Other Links \U0001f448',
        value=f'\u2022 [**Source Code**]({GITHUB})\n'
              f'\u2022 [**Invite Me!**]({INVITE})'
    )
    embed.set_footer(
        text=f'\U0001f40d discord.py v{discord.__version__}\n'
             'Thanks to redkid.net for the default templates!'
    )
    await ctx.send(embed=embed)


if __name__ == '__main__':
    bot.run(TOKEN)
