from discord.ext import commands
import discord
import time
from urllib.parse import urlencode
from humanize import precisedelta
from cogs.menus import ViewMenu


class Misc(commands.Cog, description='Other commands that are irrelevant from the main stuff.'):

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
        """Gives feedback to the dev.|<your feedback>"""

        embed = discord.Embed(
            title='New Feedback!',
            description=f'`{user_feedback}`',
            color=ctx.author.color
        )
        embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar.with_format(format='png')))
        embed.set_footer(text=f'Guild ID: {ctx.guild.id}')
        await self.bot.get_channel(765759417010225192).send(embed=embed)
        await ctx.send(':thumbsup: Your feedback has been sent!')

    @commands.command()
    async def invite(self, ctx):
        """Gives the link to invite the bot."""

        await ctx.send(f'<{self.INVITE}>')

    @commands.command()
    async def support(self, ctx):
        """Gives the link to the support server."""

        await ctx.send('https://discord.gg/fDjtZYW')

    @commands.command()
    async def about(self, ctx):
        """Gives some overall information of the bot's current state."""
        
        await ctx.send(f'Servers: `{len(self.bot.guilds)}`\n'
                       f'Uptime: {precisedelta(time.time() - self.bot.up_at)}\n'
                       f'Channels: `{len(list(self.bot.get_all_channels()))}`\n'
                       f'WS Ping: `{round(self.bot.latency * 1000)}ms`')

    @commands.command()
    async def ping(self, ctx):
        """Gives the WS, API, and round trip latency of the bot."""

        websocket = round(self.bot.latency * 1000, 2)
        t1 = time.perf_counter()
        message = await ctx.send('Pinging...')
        t2 = time.perf_counter()
        api = round((t2 - t1) * 1000, 2)
        ca = ctx.message.created_at
        rnd = round((discord.utils.utcnow() - ca)
                    .total_seconds() * 1000, 2)
        embed = discord.Embed(
            color=ctx.me.color
        )
        embed.add_field(name='Websocket', value=f'`{websocket}ms`')
        embed.add_field(name='API', value=f'`{api}ms`')
        embed.add_field(name='Round Trip', value=f'`{rnd}ms`')
        await message.edit(content=None, embed=embed)

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def urban(self, ctx, *, term):
        """Looks up a word in the urban dictionary|<word/term to look up>"""

        async with self.bot.session.get(self.URBAN + '?' + urlencode({'term': term})) as resp:
            if resp.status != 200:
                return await ctx.send(f':no_entry: `{resp.status}` Something went wrong...')
            data = await resp.json()

        try:
            data = data['list']
        except (KeyError, IndexError):
            return await ctx.send(f':no_entry: Definition not found.')

        embeds = []
        for entry in data:
            embed = discord.Embed(
                title=entry['word'],
                url=entry['permalink'],
                description='**' + entry['definition'].replace('[', '').replace(']', '') + '**',
                color=ctx.author.color
            )
            embed.add_field(name='\u200b', value=f'*{entry["example"]}*'.replace('[', '').replace(']', ''), inline=False)
            embed.set_footer(text=f'By {entry["author"]}')
            embed.add_field(name='\U0001f44d', value=str(entry['thumbs_up']))
            embed.add_field(name='\U0001f44e', value=str(entry['thumbs_down']))
            embeds.append(embed)

        view = ViewMenu(ctx, embeds)
        await ctx.send(embed=embeds[0], view=view)
        await view.wait()

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        """Nothing to see here."""
        try:
            status = await self.bot.db.execute(query)
        except Exception as error:
            return await ctx.send(f'```diff\n- {error}```')
        await ctx.send(f'```sql\n{status}```')


def setup(bot):
    bot.add_cog(Misc(bot))
