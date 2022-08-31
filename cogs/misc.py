from discord.ext import commands
from discord import app_commands
import discord
import time
from urllib.parse import urlencode
from cogs.menus import ViewMenu
from cogs.help import send_bot_help


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ICON = 'https://media.discordapp.net/attachments/742973400636588056/745710912257916950/159607234227809532.png'
        self.INVITE = 'https://discord.com/api/oauth2/authorize?client_id=742921922370600991&permissions=274877991936&scope=bot%20applications.commands'
        self.GITHUB = 'https://github.com/Stormtorch002/MadLibs'
        self.URBAN = 'https://api.urbandictionary.com/v0/define'
        self.FOOTER_ICON = 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png'
        self.TOP_GG = 'https://top.gg/bot/742921922370600991/vote'
        self.cooldowns = []

    @app_commands.command(name='help')
    async def help_command(self, interaction):
        """Shows all the commands."""
        await send_bot_help(interaction)

    @app_commands.command()
    @app_commands.describe(feedback='the feedback to send')
    @app_commands.checks.cooldown(2, 60)
    async def feedback(self, interaction, feedback: str):
        """Gives feedback to the dev."""

        embed = discord.Embed(
            title='New Feedback!',
            description=f'`{feedback}`',
            color=interaction.user.color
        )
        embed.set_author(name=str(interaction.user), icon_url=str(interaction.user.avatar.with_format('png')))
        embed.set_footer(text=f'Guild ID: {interaction.guild.id}')
        await self.bot.get_channel(765759417010225192).send(embed=embed)
        await interaction.response.send_message(':thumbsup: Your feedback has been sent!')

    @app_commands.command()
    async def invite(self, interaction):
        """Gives the link to invite the bot."""

        await interaction.send(f'<{self.INVITE}>')

    @app_commands.command()
    async def support(self, interaction):
        """Gives the link to the support server."""

        await interaction.response.send_message('https://discord.gg/fDjtZYW')

    @app_commands.command()
    async def about(self, interaction):
        """Gives some overall information of the bot's current state."""

        textchannels = [c for c in self.bot.get_all_channels() if c.type is discord.ChannelType.text]

        embed = discord.Embed(
            color=interaction.user.color
        ).add_field(
            name='Servers',
            value=f'`{len(self.bot.guilds)}`',
            inline=False
        ).add_field(
            name='Channels',
            value=f'`{len(textchannels)}`',
            inline=False
        ).add_field(
            name='Last Down',
            value=f'<t:{int(self.bot.up_at)}:R>',
            inline=False
        ).add_field(
            name='Websocket Ping',
            value=f'`{round(self.bot.latency * 1000)}ms`',
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.checks.cooldown(1, 10)
    async def ping(self, interaction):
        """Gives the WS and API latency of the bot."""

        websocket = round(self.bot.latency * 1000, 2)
        t1 = time.perf_counter()
        await interaction.response.send_message('Pinging...')
        t2 = time.perf_counter()
        api = round((t2 - t1) * 1000, 2)
        embed = discord.Embed(
            color=interaction.guild.me.color
        )
        embed.add_field(name='Websocket', value=f'`{websocket}ms`')
        embed.add_field(name='API', value=f'`{api}ms`')
        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command()
    @app_commands.describe(word='the search term to look up')
    @app_commands.checks.cooldown(2, 10)
    async def urban(self, interaction, word: str):
        """Looks up a word in the urban dictionary"""

        async with self.bot.session.get(self.URBAN + '?' + urlencode({'term': word})) as resp:
            if resp.status != 200:
                return await interaction.response.send_message(f':no_entry: `{resp.status}` Something went wrong...')
            data = await resp.json()

        try:
            data = data['list']
        except (KeyError, IndexError):
            return await interaction.response.send_message(f':no_entry: Definition not found.')

        embeds = []
        for entry in data:
            embed = discord.Embed(
                title=entry['word'],
                url=entry['permalink'],
                description='**' + entry['definition'].replace('[', '').replace(']', '') + '**',
                color=interaction.user.color
            )
            embed.add_field(name='\u200b', value=f'*{entry["example"]}*'.replace('[', '').replace(']', ''),
                            inline=False)
            embed.set_footer(text=f'By {entry["author"]}')
            embed.add_field(name='\U0001f44d', value=str(entry['thumbs_up']))
            embed.add_field(name='\U0001f44e', value=str(entry['thumbs_down']))
            embeds.append(embed)

        view = ViewMenu(interaction, embeds)
        view.message = await interaction.response.send_message(embed=embeds[0], view=view)
        await view.wait()

    # @commands.group(invoke_without_command=True)
    # @commands.is_owner()
    # async def sql(self, interaction, *, query):
    #     """Nothing to see here."""
    #     try:
    #         status = await self.bot.db.execute(query)
    #     except Exception as error:
    #         return await interaction.response.send_message(f'```diff\n- {error}```')
    #     await interaction.response.send_message(f'```sql\n{status}```')


async def setup(bot):
    await bot.add_cog(Misc(bot))
