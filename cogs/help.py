import discord

icon_url = 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png'
thumb_url = 'https://c.tenor.com/omJbisofB98AAAAC/pepe-clown.gif'
robux = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'


async def send_bot_help(interaction):
    embed = discord.Embed(
        title='MadLibs Commands',
        color=interaction.user.color,
        description='Hello! I am a bot made by **Stormtorch#1128**! '
                    'Commands are listed below.'
    ).set_footer(
        text=f'Default templates: redkid.net\nMade with discord.py v{discord.__version__}',
        icon_url=icon_url
    ).set_thumbnail(
        url=thumb_url
    )
    cogs = {
        'Playing MadLibs': [
            '/madlibs',
            '/custom  . . .',
            '/history',
            '/pos',
        ],
        'Other': [
            '/feedback',
            '/invite',
            '/vote',
            '/support',
            '/about',
            '/ping',
            '/urban'
        ]
    }

    for cog, cmds in cogs.items():
        cmds = '\n'.join([f'[**{cmd}**]({robux})' for cmd in cmds])
        if cmds:
            embed.add_field(name=cog, value=cmds)

    links = {
        'Add MadLibs': 'https://discord.com/oauth2/authorize?client_id=742921922370600991&permissions=19521&scope=bot',
        'Support': 'https://discord.gg/xFvqDVxjj2',
        'Vote': 'https://top.gg/bot/742921922370600991/vote',
        'Source': 'https://github.com/Stormtorch002/MadLibs'
    }
    view = discord.ui.View()
    for name, url in links.items():
        button = discord.ui.Button(label=name, url=url, style=discord.ButtonStyle.blurple)
        view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)


