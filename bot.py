from database import db as db_file
from discord.ext import commands
from config import TOKEN, PASTEBIN_API_KEY
import discord
from aiohttp import ClientSession

db, prefixes = db_file.db, db_file.prefixes


def get_prefix(client, message):
    prefix = prefixes.get(message.guild.id)
    return prefix if prefix else 'ml!'


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')
bot.db = db
bot.prefixes = prefixes
bot.fetchone, bot.fetchall, bot.execute = db_file.fetchone, db_file.fetchall, db_file.execute

for cog in ('config', 'listeners', 'madlibs'):
    bot.load_extension('cogs.' + cog)
bot.load_extension('jishaku')


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
    else:
        print(error)


@bot.command()
async def invite(ctx):
    await ctx.send(f'**You can invite me here:**\n'
                   f'<https://discord.com/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot>')


@bot.command()
async def pastebin(ctx, *, text):
    data = {
        'api_dev_key': PASTEBIN_API_KEY,
        'api_option': 'paste',
        'api_paste_code': text,
        'api_paste_name': f"{ctx.author}'s Paste"
    }
    async with ClientSession() as session:
        async with session.post('https://pastebin.com/api/api_post.php', data=data) as resp:
            await ctx.send(await resp.text())


@bot.command(name='help', aliases=['cmds', 'commands'])
async def _help(ctx):
    if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
        return await ctx.send('I need the `Embed Links` permission to display help.')

    embed = discord.Embed(color=discord.Colour.blue())
    embed.title = f'Commands'
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/742973400636588056/745710912257916950/'
                            '159607234227809532.png')
    embed.description = f'[Source Code](https://github.com/Stormtorch002/MadLibs)\n[Invite](https://discord.com/' \
                        f'oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot)'
    p = ctx.prefix

    cmds = {
        f"{p}**prefix**": 'Shows/changes the current server prefix',
        f"{p}**invite**": 'Sends my invite link!',
        f"{p}**madlibs**": 'Lets you host a MadLibs game',
        f"{p}**plays**": "Gets a play from the history of the server's laughable moments",
        f"{p}**custom**": 'Manages custom story templates for the current server',
        f"{p}**feedback**": "Gives feedback about anything related to the bot, including source code",
        f"{p}**pastebin**": "Not really relevant but creates a pastebin paste and sends you the URL.",
    }

    for cmd in cmds.keys():
        embed.add_field(name=cmd, value=cmds[cmd], inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)
