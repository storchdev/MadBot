from discord.ext import commands
from datetime import datetime
import discord
import time
from urllib.parse import quote


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ICON = 'https://media.discordapp.net/attachments/' \
                    '742973400636588056/745710912257916950/159607234227809532.png'
        self.INVITE = 'https://discord.com/oauth2/authorize?' \
                      'client_id=742921922370600991&permissions=19521&scope=bot'
        self.GITHUB = 'https://github.com/Stormtorch002/MadLibs'
        self.URBAN = 'https://api.urbandictionary.com/v0/define'
        self.FOOTER_ICON = 'https://cdn.discordapp.com/icons/' \
                           '336642139381301249/3aa641b21acded468308a37eef43d7b3.png'
        self.TOP_GG = 'https://top.gg/bot/742921922370600991/vote'

    @commands.command()
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def feedback(self, ctx, *, user_feedback):
        embed = discord.Embed(
            title='New Feedback!',
            description=f'`{user_feedback}`',
            color=ctx.author.color
        )
        embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url_as(format='png')))
        embed.set_footer(text=f'Guild ID: {ctx.guild.id}')
        await self.bot.get_channel(765759417010225192).send(embed=embed)
        await ctx.send(':thumbsup: Your feedback has been sent!')

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(f'**You can invite me here:**\n<{self.INVITE}>')

    @commands.command()
    async def support(self, ctx):
        await ctx.send('https://discord.gg/fDjtZYW')

    @commands.command()
    async def ping(self, ctx):
        websocket = round(self.bot.latency * 1000, 2)
        t1 = time.perf_counter()
        message = await ctx.send('Pinging...')
        t2 = time.perf_counter()
        api = round((t2 - t1) * 1000, 2)
        rnd = round((datetime.utcnow() - ctx.message.created_at)
                    .total_seconds() * 1000, 2)
        embed = discord.Embed(
            color=ctx.me.color
        )
        embed.add_field(name='Websocket', value=f'`{websocket}ms`', inline=False)
        embed.add_field(name='API', value=f'`{api}ms`', inline=False)
        embed.add_field(name='Round Trip', value=f'`{rnd}ms`', inline=False)
        await message.edit(content=None, embed=embed)

    @commands.command(name='help', aliases=['cmds', 'commands'])
    async def _help(self, ctx):
        embed = discord.Embed(
            title='MadLibs Commands List',
            description='Hello! I am a bot made by **Stormtorch#8984**! '
                        'Commands are listed below with brief descriptons.\n\n'
                        f'**It would be greatly appreciated if you could vote for me [here]({self.TOP_GG})!',
            color=discord.Colour.blue() if ctx.me.color == discord.Colour.default() else ctx.me.color
        )
        p = (self.bot.prefixes.get(ctx.guild.id) or 'ml!').lower()

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
            value=f'\u2022 [**Source Code**]({self.GITHUB})\n'
                  f'\u2022 [**Invite Me!**]({self.INVITE})\n'
                  f'\u2022 [**Vote for Me!**]({self.TOP_GG})'
        )
        embed.set_footer(
            text=f'\U0001f40d discord.py v{discord.__version__}\n'
                 'Thanks to redkid.net for the default templates!',
            icon_url=self.FOOTER_ICON
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def urban(self, ctx, index: commands.Greedy[int], *, term=None):
        if not term:
            return await ctx.send(f':no_entry: You need to provide a word to look up!')
        index = 0 if not index else index[0]

        async with self.bot.session.get(self.URBAN, params={'term': quote(term)}) as resp:
            if resp.status != 200:
                return await ctx.send(f':no_entry: `{resp.status}` Something went wrong...')
            data = await resp.json()

        try:
            data = data['list'][index]
        except (KeyError, IndexError):
            return await ctx.send(f':no_entry: Definition not found.')

        embed = discord.Embed(
            title=data['word'],
            url=data['permalink'],
            description='**' + data['definition'].replace('[', '').replace(']', '') + '**',
            color=discord.Colour.blue()
        )
        embed.add_field(name='\u200b', value=f'*{data["example"]}*'.replace('[', '').replace(']', ''), inline=False)
        embed.set_footer(text=f'By {data["author"]}')
        embed.add_field(name='\U0001f44d', value=str(data['thumbs_up']))
        embed.add_field(name='\U0001f44e', value=str(data['thumbs_down']))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        try:
            status = await self.bot.db.execute(query)
        except Exception as error:
            return await ctx.send(f'```diff\n- {error}```')
        await ctx.send(f'```sql\n{status}```')


def setup(bot):
    bot.add_cog(Misc(bot))
