from discord.ext import commands
from discord import app_commands
import discord
import time
from urllib.parse import urlencode
from cogs.menus import ViewMenu


HELP_FOOTER_ICON = 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png'
HELP_THUMBNAIL = 'https://c.tenor.com/omJbisofB98AAAAC/pepe-clown.gif'

INVITE = 'https://discord.com/api/oauth2/authorize?client_id=1059565201457946655&permissions=274877991936&scope=bot%20applications.commands'
GITHUB = 'https://github.com/Stormtorch002/MadBot'
URBAN = 'https://api.urbandictionary.com/v0/define'
TOP_GG = 'https://top.gg/bot/1059565201457946655/vote'
SUPPORT = 'https://discord.gg/fDjtZYW'


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help')
    async def help_command(self, interaction):
        """Shows all the commands."""
        embed = discord.Embed(
            title='MadBot Commands',
            color=interaction.user.color,
            description='Hello! I am a bot made by **stormtorch**! '
                        'Commands are listed below.'
        ).set_footer(
            text=f'Default templates: redkid.net\nMade with discord.py v{discord.__version__}',
            icon_url=HELP_FOOTER_ICON
        ).set_thumbnail(
            url=HELP_THUMBNAIL
        )
        cogs = {
            'Playing Mad Libs': [
                'madlibs',
                'history',
                'pos',
                'incognito'
            ],
            'Custom Stories': [
                'custom add',
                'custom edit',
                'custom delete',
                'custom list',
                'custom info',
                'custom import'
            ],
            'Other': [
                'feedback',
                'invite',
                'vote',
                'support',
                'about',
                'ping',
                'urban'
            ]
        }

        if interaction.user.guild_permissions.administrator:
            cogs['Settings (Admin Only)'] = [
                'settings time-limit',
                'settings max-players',
                'settings max-games',
                'settings reset',
                'settings show-entered',
                'settings mention-players',
                'clear-history',
            ]

        for cog, names in cogs.items():
            lines = []

            for name in names:
                for cmd in interaction.client.app_commands:
                    if name.startswith(cmd.name):
                        lines.append(f'</{name}:{cmd.id}>')
                        break 

            cmds = '\n'.join(lines)
            embed.add_field(name=cog, value=cmds)

        links = {
            'Add MadBot': INVITE,
            'Support': SUPPORT,
            'Vote': TOP_GG,
            'Source': GITHUB
        }

        view = discord.ui.View()
        for name, url in links.items():
            button = discord.ui.Button(label=name, url=url)
            view.add_item(button)

        await interaction.response.send_message(embed=embed, view=view)

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
        embed.set_author(name=str(interaction.user), icon_url=str(interaction.user.display_avatar.with_format('png')))
        embed.set_footer(text=f'Guild ID: {interaction.guild.id}')

        await self.bot.get_channel(765759417010225192).send(embed=embed)
        await interaction.response.send_message(':thumbsup: Your feedback has been sent!')

    @app_commands.command()
    async def invite(self, interaction):
        """Gives the link to invite the bot."""

        await interaction.response.send_message(f'<{INVITE}>')

    @app_commands.command()
    async def support(self, interaction):
        """Gives the link to the support server."""

        await interaction.response.send_message(SUPPORT)

    @app_commands.command()
    async def vote(self, inter):
        """Sends the link to vote for the bot on top.gg."""

        await inter.response.send_message(F'{TOP_GG}\n\n**Thanks for your support!**')

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

        async with self.bot.session.get(URBAN + '?' + urlencode({'term': word})) as resp:
            if resp.status != 200:
                return await interaction.response.send_message(f':no_entry: `{resp.status}` Something went wrong...')
            data = await resp.json()

        data = data['list']
        if len(data) == 0:
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


async def setup(bot):
    await bot.add_cog(Misc(bot))
