import discord
from discord.ext import commands

icon_url = 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png'
thumb_url = 'https://uploads-ssl.webflow.com/5ed7118d4bcece1f6a97f6d3/5ef3c514d38ff63fb4fe48c3_Mad%20Libs.png'
allowed_cogs = ['top.gg', 'MadLibs', 'Misc', 'Config', 'Parts of Speech']


class HelpCommand(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        prefix = self.context.clean_prefix

        embed = discord.Embed(
            title='MadLibs Commands',
            color=self.context.author.color,
            description='Hello! I am a bot made by **Stormtorch#8984**! '
                        'Commands are listed below.'
        ).set_footer(
            text=f'Do {prefix}help <command> for more info\ndiscord.py v{discord.__version__}',
            icon_url=icon_url
        ).set_thumbnail(
            url=thumb_url
        )

        for cog, cmds in mapping.items():
            if cog is not None and cog.qualified_name in allowed_cogs:
                cmds = await self.filter_commands(cmds, sort=True)
                cmds = '\n'.join([f'`{prefix}{cmd.name}`' for cmd in cmds])
                embed.add_field(name=cog.qualified_name, value=cmds)
        invite = 'https://discord.com/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot'
        embed.add_field(name='Other Links',
                        value=f'\u2022 [**Support Server!**](https://discord.gg/xFvqDVxjj2)\n'
                              f'\u2022 [**Invite Me!**]({invite})\n'
                              f'\u2022 [**Vote for Me!**](https://top.gg/bot/742921922370600991/vote)\n'
                              f'\u2022 [**Source Code**](https://github.com/Stormtorch002/MadLibs)'
                        )
        await self.context.send(embed=embed)

    async def send_cog_help(self, cog):
        if cog.qualified_name not in allowed_cogs:
            return await self.context.send(':no_entry: Cog not found.')

        prefix = self.context.clean_prefix
        name = cog.qualified_name
        if name == 'MadLibs':
            name = 'Game'

        embed = discord.Embed(
            title=f'{name} Commands',
            color=self.context.author.color,
            description=cog.description
        ).set_footer(
            text=f'Do {prefix}help <command> for more info\ndiscord.py v{discord.__version__}',
            icon_url=icon_url
        )
        cmds = await self.filter_commands(cog.get_commands(), sort=True)
        for cmd in cmds:
            embed.add_field(name=prefix + cmd.name, value=cmd.help.split('|')[0])
        await self.context.send(embed=embed)

    def command_not_found(self, string):
        return f':no_entry: Command `{string}` doesn\'t exist.'

    async def send_group_help(self, group: commands.Group):
        if group.qualified_name == 'custom':
            await group.invoke(self.context)

    async def send_command_help(self, command: commands.Command):
        prefix = self.context.clean_prefix
        embed = discord.Embed(colour=self.context.author.color)
        embed.title = f'{prefix}{command.qualified_name}'
        h = command.help.split('|')
        if len(h) > 1:
            help_text = h[0]
            usage = h[1]
            usage = f'{prefix}{command.name}{usage}'
            embed.add_field(name='Usage', value=f'`{usage}`')
        else:
            help_text = command.help
        embed.description = help_text
        embed.set_footer(text=f'discord.py v{discord.__version__}', icon_url=icon_url)
        await self.context.send(embed=embed)


def setup(bot):
    bot._original_help_command = bot.help_command
    bot.help_command = HelpCommand()


def teardown(bot):
    bot.help_command = bot._original_help_command
