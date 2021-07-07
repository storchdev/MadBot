from discord.ext import commands
import discord
import time
import asyncio
import re
import json
from cogs.menus import TemplatesMenu, YesNo
from cogs.utils import capitalize, readable

is_vowel = re.compile('^([aeiou])')
cross_mark = '\U0000274c'


class MadLibs(commands.Cog, description='The main functionality of the bot. Play and customize games with friends!'):

    def __init__(self, bot):
        self.bot = bot
        self.finder = self.bot.finder
        self.cancelled = {}

        with open('./cogs/json/defaults.json') as f:
            self.defaults = json.load(f)
            self.lengths = {}
            self.templates = {}
            self.names = {}
            self.defaults_select = {0: {}}
            i = 1
            pages_len = 0

            self.pages = []
            page = ''
            for name in self.defaults:
                length = len(self.finder.findall(self.defaults[name]))
                # self.templates[i] = self.defaults[name]
                # self.names[i] = name
                line = f'`{i}.` **{name}** ({length} blanks)\n'
                self.defaults_select[pages_len][i] = (name, self.defaults[name])
                page += line
                if len(page) + len(line) > 500:
                    self.pages.append(page)
                    page = ''
                    pages_len += 1
                    self.defaults_select[pages_len] = {}

                i += 1

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def madlibs(self, ctx):
        """Starts a MadLibs game with you as the host."""

        self.cancelled[ctx] = False
        participants = [ctx.author]

        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label='Join Game!', style=discord.ButtonStyle.green)
        button2 = discord.ui.Button(label='Leave Game', style=discord.ButtonStyle.red)
        button3 = discord.ui.Button(label='Start Game!', style=discord.ButtonStyle.blurple, row=2)
        button4 = discord.ui.Button(label='Cancel Game', style=discord.ButtonStyle.red, row=2)

        async def join_callback(interaction):
            u = interaction.user
            if u not in participants:
                participants.append(u)
                await ctx.send(f':tada: {u.mention} has joined the game!')
            else:
                await ctx.send(f':no_entry: {u.mention}, you are already in the game.')

        async def leave_callback(interaction):
            u = interaction.user
            if u in participants:
                if u == ctx.author:
                    await ctx.send(f':no_entry: {u.mention}, hosts cannot leave the game.')
                else:
                    participants.remove(u)
                    await ctx.send(f':wave: {u.mention} has left the game.')
            else:
                await ctx.send(f':no_entry: {u.mention}, you are not in the game yet.')

        async def start_callback(interaction):
            u = interaction.user
            if u != ctx.author:
                return
            self.bot.dispatch('game_start', u)

        async def cancel_callback(interaction):
            u = interaction.user
            if u != ctx.author:
                return
            self.cancelled[ctx] = True
            view.clear_items()
            await view.message.edit(view=view)
            await ctx.send('I have cancelled the game.')

        button.callback = join_callback
        button2.callback = leave_callback
        button3.callback = start_callback
        button4.callback = cancel_callback

        for b in [button, button2, button3]:  # add button4 later maybe
            view.add_item(b)

        embed = discord.Embed(
            title='A MadLibs game is starting in this channel!',
            description=f"{ctx.author.mention}, start the game whenever you're ready.",
            color=discord.Colour.green()
        )
        view.message = await ctx.send(embed=embed, view=view)
        try:
            await self.bot.wait_for('game_start', check=lambda u: u == ctx.author, timeout=180)
            if self.cancelled[ctx]:
                return
        except asyncio.TimeoutError:
            if self.cancelled[ctx]:
                return
            await ctx.send(f':alarm_clock: {ctx.author.mention} did not start the game, so I am doing it for them.')

        view.children[2].disabled = True
        await view.message.edit(view=view)

        i = 1
        defaults = []
        for page in self.pages:
            embed = discord.Embed(
                title=f'Default Templates - Page {i}/{len(self.pages)}',
                color=ctx.author.color,
                description=page
            )
            defaults.append(embed)
            i += 1

        customs = []
        customs_select = {0: {}}
        pages_len = 0
        i = 1

        query = 'SELECT name, template FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, ctx.guild.id)

        pages = []
        page = ''
        for row in rows:
            name = row["name"]
            customs_select[pages_len][i] = (name, row['template'])
            blanks = len(self.finder.findall(row['template']))
            line = f'`{i}.` **{name}** ({blanks} blanks)'

            page += line
            if len(page) + len(line) > 500:
                pages.append(page)
                page = ''
                pages_len += 1
                customs_select[pages_len] = {}

            i += 1
        i = 1
        for page in pages:
            embed = discord.Embed(
                title=f'Custom Templates - Page {i}/{len(pages)}',
                color=ctx.author.color,
                description=page
            )
            customs.append(embed)

        await ctx.send(embed=defaults[0],
                       view=TemplatesMenu(
                           ctx, defaults, customs, self.defaults_select, customs_select
                       ))

        def check(u, n, t):
            return u == ctx.author

        select = await self.bot.wait_for('select', check=check)
        if self.cancelled[ctx]:
            return

        template_name = select[1]
        final_story = select[2]
        blanks = self.finder.findall(final_story)

        progress = 1
        total = len(blanks)
        while True:
            blank = blanks[progress - 1]

            try:
                user = participants[0]
            except IndexError:
                return await ctx.send(f'Nobody is left in the game. It has been canceled.')

            opt = 'n' if is_vowel.match(blank) else ''
            hint = ' (NOT ENDING IN "ING")' if blank.lower() == 'verb' else ''
            await ctx.send(f'{user.mention}, type out a{opt} **{blank}{hint}**. ({progress}/{total})')

            def check(m):
                return m.channel.id == ctx.channel.id and m.author.id == user.id

            try:
                message = await self.bot.wait_for('message', check=check, timeout=30)
                if self.cancelled[ctx]:
                    return
                participants.pop(0)

                if len(message.content) > 100:
                    await ctx.send(f':no_entry: Your word must be 100 characters or under. Skipping your turn.')
                    participants.append(message.author)
                else:
                    participants.append(message.author)
                    final_story = final_story.replace(f'{{{blank}}}', message.content, 1)

                    if progress == total:
                        break

                    progress += 1
            except asyncio.TimeoutError:
                if self.cancelled[ctx]:
                    return
                try:
                    participants.remove(user)
                    await ctx.send(f'\u23f0 {user.mention} has been removed from the game due to inactivity.')
                except ValueError:
                    continue

        for button in view.children:
            button.disabled = True
        await view.message.edit(view=view)

        pids = [p.id for p in participants]

        query = 'UPDATE madlibs SET plays = plays + 1 WHERE guild_id = $1 AND name = $2'
        await self.bot.db.execute(query, ctx.guild.id, template_name)
        query = 'INSERT INTO plays (channel_id, participants, final_story, played_at, name, guild_id) ' \
                'VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(
            query,
            ctx.channel.id,
            json.dumps(pids, indent=4),
            final_story,
            int(time.time()),
            template_name,
            ctx.guild.id
        )

        embedded_story = ''
        pages = []
        final_story = capitalize(final_story)

        for word in final_story.split():
            word += ' '

            if len(word + embedded_story) > 2048:
                pages.append(embedded_story)
                embedded_story = ''
            else:
                embedded_story += word
        pages.append(embedded_story)

        if ctx.author.id in pids:
            view = YesNo(ctx, template_name, final_story, participants)
            view.message = await ctx.send(
                f'{ctx.author.mention}, would you like to send this result to my support server? '
                'I will not be sharing anything except your usernames and the final product.',
                view=view)
            await view.wait()

        message = await ctx.send(f'Grand finale in **3...**')
        await asyncio.sleep(1)
        await message.edit(content='Grand finale in **2...**')
        await asyncio.sleep(1)
        await message.edit(content='Grand finale in **1...**')
        await asyncio.sleep(1)

        i = 0
        names = ", ".join([user.display_name for user in participants])
        for page in pages:
            embed = discord.Embed(description=page, color=ctx.author.color)
            embed.set_footer(text='By ' + names)
            if i == 0:
                embed.title = template_name
            await message.edit(content=None, embed=embed)
            i += 1

    @commands.group(invoke_without_command=True)
    async def custom(self, ctx):
        p = ctx.prefix.lower()
        embed = discord.Embed(
            title='Custom Templates',
            description='Custom templates are a great way to customize your experience. '
                        'If you have a MadLibs book, you can copy a story from there, or make your own!',
            color=ctx.me.color
        )
        embed.add_field(
            name=f'\U0001f6e0 {p}custom **add** *"<name>" <template>*',
            value=f'Adds a custom template to the server. Example:\n'
                  f'`{p}custom add "example" The {{noun}} is {{adjective}}.`'
        )
        embed.add_field(
            name=f'\U0001f4e5 {p}custom **import** *<server ID> <name>*',
            value='Imports a custom template from another server.'
        )
        embed.add_field(
            name=f'\U0001f5d1 {p}custom **delete** *<name>*',
            value='Deletes a custom template. You must have created it, or have `Manage Server` perms.'
        )
        embed.add_field(
            name=f'\U0001f4dd {p}custom **edit** *"<name>" <new version>*',
            value='Edits a custom template; requires same permissions as deleting.'
        )
        embed.add_field(
            name=f'\U0001f50d {p}custom **info** *<name>*',
            value='Gets info on a custom template.'
        )
        embed.add_field(
            name=f'\U0001f4f0 {p}custom **all**',
            value='Lists all custom templates'
        )
        await ctx.send(embed=embed)

    @custom.command(name='add', aliases=['create'])
    async def _add(self, ctx, name, *, template):
        """Adds a new custom template to the server.|<template name> <template contents>"""

        name = name.strip(' ')
        if len(name) > 32:
            return await ctx.send(f':no_entry: The name of the template must be 32 characters or under.')

        template = template.strip(' ')

        if not len(self.finder.findall(template)):
            return await ctx.send(
                f':no_entry: Make sure to include **at least one blank** in the template. '
                'Blanks are placeholders marked with curly brackets, like `{noun}`.'
            )

        query = 'SELECT id FROM madlibs WHERE name = $1 AND guild_id = $2'
        exists = await self.bot.db.fetchrow(query, name, ctx.guild.id)

        if exists:
            return await ctx.send(
                f':no_entry: A custom template with name `{name}` already exists in this guild.'
            )

        query = 'INSERT INTO madlibs (name, template, guild_id, creator_id, plays, created_at) ' \
                'VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(query, name, template, ctx.guild.id, ctx.author.id, 0, int(time.time()))
        await ctx.send(f':thumbsup: Successfully added custom story template with name `{name}`!')

    @custom.command(name='delete', aliases=['remove', 'nize'])
    async def _delete(self, ctx, *, name):
        """Deletes an existing custom template from the server.|<template name>"""

        query = 'SELECT creator_id FROM madlibs WHERE name = $1 AND guild_id = $2'
        creator_id = await self.bot.db.fetchrow(query, name, ctx.guild.id)

        if creator_id:
            creator_id = creator_id['creator_id']

            if ctx.author.id != creator_id and not ctx.author.guild_permissions.manage_guild:
                return await ctx.send(':no_entry: You are not authorized to delete this tag.')

            query = 'DELETE FROM madlibs WHERE name = $1 AND guild_id = $2'
            await self.bot.db.execute(query, name, ctx.guild.id)

            await ctx.send(f':thumbsup: Successfully deleted custom story template {name}.')
        else:
            await ctx.send(f':no_entry: No custom template with name `{name}` found.')

    @custom.command(name='edit')
    async def _edit(self, ctx, name, *, edited):
        """Edits an existing custom template.|<template name> <new contents>"""

        query = 'SELECT creator_id FROM madlibs WHERE name = $1 AND guild_id = $2'
        creator_id = await self.bot.db.fetchrow(query, name, ctx.guild.id)

        if not creator_id:
            return await ctx.send(f':no_entry: No custom template with name `{name}` found.')

        creator_id = creator_id['creator_id']

        if ctx.author.id != creator_id and not ctx.author.guild_permissions.manage_guild:
            return await ctx.send(f':no_entry: You are not authorized to edit this tag.')

        query = 'UPDATE madlibs SET template = $1 WHERE name = $2 AND guild_id = $3'
        await self.bot.db.execute(query, edited, name, ctx.guild.id)
        await ctx.send(f':thumbsup: Successfully edited custom story template `{name}`.')

    @custom.command(name='all')
    async def _all(self, ctx):
        """Lists all the custom templates in the server."""

        query = 'SELECT name FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, ctx.guild.id)

        if not rows:
            return await ctx.send(f':no_entry: No custom templates found in this guild.')

        await ctx.send("**All Custom Templates:**\n\n" + '\n'.join(['`' + row['name'] + '`' for row in rows]))

    @custom.command(name='info')
    async def _info(self, ctx, *, name):
        """Gets info on a custom template.|<template name>"""

        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(f':no_entry: I need the `Embed Links` permission to send info.')

        query = 'SELECT template, creator_id, plays, created_at FROM madlibs WHERE guild_id = $1 AND name = $2'
        row = await self.bot.db.fetchrow(query, ctx.guild.id, name)

        if not row:
            return await ctx.send(f':no_entry: No template called `{name}` was found.')

        embed = discord.Embed(
            title=name,
            color=discord.Colour.blue()
        )
        embed.add_field(name='Number of Plays', value=f'**{row["plays"]}**')

        user = ctx.guild.get_member(row['creator_id'])
        if not user:
            embed.add_field(name='Creator', value=f'<@{row["creator_id"]}>\n(not in server)')
        else:
            embed.add_field(name='Creator', value=f'{user.mention}')
            embed.set_author(name=str(user), icon_url=str(user.avatar.with_format(format='png')))

        blanks = self.finder.findall(row['template'])
        embed.add_field(name='Number of Blanks', value=f'**{len(blanks)}**')

        if row['created_at']:
            created_at = readable(row['created_at'])
            embed.add_field(name='Created At', value=created_at)

        if len(blanks) <= 1024:
            embed.add_field(name='Blanks', value=', '.join(blanks))

        await ctx.send(embed=embed)

    @custom.command(name='import')
    async def _import(self, ctx, guild_id: int, *, name):
        """Imports a custom template from another guild. You will be the owner of it in this server.|
        <server ID> <template name>"""

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send(f':no_entry: Could not find server with ID `{guild_id}`.')

        query = 'SELECT template FROM madlibs WHERE guild_id = $1 AND name = $2'
        row = await self.bot.db.fetchrow(query, guild_id, name)
        if not row:
            return await ctx.send(f":no_entry: The template with name `{name}` doesn't exist in that server.")

        template = row['template']
        row = await self.bot.db.fetchrow(query, ctx.guild.id, name)
        if row:
            return await ctx.send(f':no_entry: A template with the name `{name}` already exists.')

        query = 'INSERT INTO madlibs (name, template, guild_id, creator_id, plays, created_at) ' \
                'VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(query, name, template, ctx.guild.id, ctx.author.id, 0, int(time.time()))
        await ctx.send(f':thumbsup: Successfully imported **{name}** from `{guild.name}`!')

    @commands.command(aliases=['history'])
    async def plays(self, ctx, index: int, *, storyname=None):
        """Fetches a completed MadLibs story from the history of this server.|
        <index (1 for the latest)> <name of story>"""

        if storyname:
            query = 'SELECT channel_id, participants, final_story, played_at, name FROM plays ' \
                    'WHERE guild_id = $1 AND name = $2'
            rows = await self.bot.db.fetch(query, ctx.guild.id, storyname)
        else:
            query = 'SELECT channel_id, participants, final_story, played_at, name FROM plays ' \
                    'WHERE guild_id = $1'
            rows = await self.bot.db.fetch(query, ctx.guild.id)

        if not rows:
            return await ctx.send('No plays found.')

        try:
            story = rows[-index]
        except IndexError:
            return await ctx.send(f':no_entry: Only `{len(rows)}` stories exist for that request.')

        final_story = story['final_story']
        if len(final_story) > 2048:
            desc = final_story[:2044] + '...'
        else:
            desc = final_story

        embed = discord.Embed(
            title=story['name'],
            description=desc,
            color=discord.Colour.blue()
        )
        participants = []
        for user_id in json.loads(story['participants']):
            user = self.bot.get_user(user_id)
            if user:
                participants.append(user.mention)
            else:
                participants.append(f'<@{user_id}>')
        mentions = ', '.join(participants)
        embed.add_field(name='Participants', value=mentions)

        ch = self.bot.get_channel(story['channel_id']).mention
        if ch:
            embed.add_field(name='Channel', value=ch)

        played_at = readable(story['played_at'])
        embed.add_field(name='Played At', value=played_at)
        await ctx.send(embed=embed)

    @_add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f':no_entry: You must provide both a **name** and a **template** for this command.'
                f'Usage: `{ctx.prefix}{ctx.invoked_with} "<name>" <template>`'
            )
        else:
            raise error

    @_edit.error
    async def edit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f':no_entry: '
                           f'You must provide both a **name** and a **new template** for this command. '
                           f'Usage: `{ctx.prefix}{ctx.invoked_with} "<name>" <new edited template>`')
        else:
            raise error

    @_delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f':no_entry: '
                           f'You must provide the **name** of the template to delete for this command.')
        else:
            raise error

    @_info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f':no_entry: '
                           f'You must provide the **name** of the template to view for this command.')
        else:
            raise error

    @plays.error
    async def plays_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or \
                isinstance(error, commands.BadArgument):
            await ctx.send(f':no_entry: '
                           f'The correct usage is: `{ctx.prefix}plays <index> <template name>`.')
        else:
            raise error

    @_import.error
    async def import_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f":no_entry: You must provide a valid server ID.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f":no_entry: "
                           f"You must provide a **server ID** and the **name of the template** "
                           f"in that server for this command.")
        else:
            raise error


def setup(bot):
    bot.add_cog(MadLibs(bot))
