from discord.ext import commands
import discord
import time
import asyncio
import re
import json
from cogs import menus
from cogs.utils import capitalize, readable

is_vowel = re.compile('^([aeiou])')
cross_mark = '\U0000274c'


class MadLibs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.finder = self.bot.finder

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

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def madlibs(self, ctx):
        p = ctx.prefix.lower()

        query = 'SELECT name, template FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, ctx.guild.id)
        total = len(self.bot.defaults) + 1

        for row in rows:
            self.bot.templates[total] = row['template']
            self.bot.names[total] = row[0]
            total += 1
        participants = [ctx.author]
        embed = discord.Embed(
            title='A MadLibs game is starting in this channel!',
            description=f'Send `join` in chat to join!',
            color=discord.Colour.green())
        embed.set_footer(
            text=f'If you are the host, please send [{p}start] to start the game, or [{p}cancel] to stop it.'
        )
        await ctx.send(embed=embed)

        timeout_in = 30
        end = time.time() + timeout_in

        def check(m):
            return m.channel.id == ctx.channel.id and (
                    m.content.lower() == 'join' and m.author.id != ctx.author.id
                    or m.content.lower() in (p + 'start', p + 'cancel')
                    and m.author.id == ctx.author.id
            )

        while True:
            try:
                message = await self.bot.wait_for('message', check=check, timeout=end - time.time())
                if message.author.id == ctx.author.id:
                    if message.content.lower() == p + 'start':
                        break
                    else:
                        return await ctx.send(f':no_entry: The game has been canceled by the host.')
                else:
                    participants.append(message.author)
                    await ctx.send(f':thumbsup: {message.author.mention} has joined the game!')
            except asyncio.TimeoutError:
                break

        pagination = {
            'on_custom': False,
            'page': 1
        }
        menu = await ctx.send(embed=(await menus.create_embed(ctx, pagination))[0])
        task = self.bot.loop.create_task(menus.menu(ctx, menu, pagination))

        async def delete_menu():
            try:
                await menu.delete()
            except discord.NotFound:
                pass

        async def end():
            await delete_menu()
            if not task.done():
                task.cancel()

        def check(m):
            if m.author.id != ctx.author.id or m.channel.id != ctx.channel.id:
                return False
            if m.content.lower() == p + 'cancel':
                return True
            if m.content.isdigit():
                if int(m.content) < total:
                    return True
            return False

        try:
            message = await self.bot.wait_for('message', check=check, timeout=120)
            await delete_menu()
            task.cancel()
            if message.content.lower() == p + 'cancel':
                return await ctx.send(f':no_entry: The game has been canceled by the host.')
            i = int(message.content)
        except asyncio.TimeoutError:
            await end()
            return await ctx.send(
                f'\u23f0 {ctx.author.mention}: You took too long to respond with a template number!'
            )

        final_story = self.bot.templates[i]
        template_name = self.bot.names[i]
        blanks = self.finder.findall(final_story)

        async def wait_for_join(game):

            def wait_check(m):
                return m.channel.id == ctx.channel.id and m.content.lower() == 'join' and \
                       m.author.id not in [player.id for player in game]

            while True:
                author = (await self.bot.wait_for('message', check=wait_check)).author
                game.append(author)
                await ctx.send(f'{author.mention} has joined the game!')

        task = self.bot.loop.create_task(wait_for_join(participants))

        progress = 1
        total = len(blanks)
        while True:
            blank = blanks[progress - 1]

            try:
                user = participants[0]
            except IndexError:
                task.cancel()
                return await ctx.send(f'Nobody is left in the game. It has been canceled.')

            opt = 'n' if is_vowel.match(blank) else ''
            await ctx.send(f'{user.mention}, type out a{opt} **{blank}**. ({progress}/{total})')

            def check(m):
                return m.channel.id == ctx.channel.id and m.author.id == user.id

            try:
                message = await self.bot.wait_for('message', check=check, timeout=30)
                participants.pop(0)

                if message.author.id == ctx.author.id and message.content.lower() == p + 'cancel':
                    await end()
                    return await ctx.send(f':no_entry: The host has canceled the game.')

                if message.content.lower() == p + 'leave':
                    await ctx.send(f'{message.author.mention} has left the game.')
                elif len(message.content) > 100:
                    await ctx.send(f':no_entry: Your word must be 100 characters or under. Skipping your turn.')
                    participants.append(message.author)
                else:
                    participants.append(message.author)
                    final_story = final_story.replace(f'{{{blank}}}', message.content, 1)

                    if progress == total:
                        break

                    progress += 1
            except asyncio.TimeoutError:
                participants.remove(user)
                await ctx.send(f'\u23f0 {user.mention} has been removed from the game due to inactivity.')

        task.cancel()
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

        send = False
        if ctx.author.id in pids:
            await ctx.send(f'{ctx.author.mention}: Would you like to send this play to my support server? '
                           'I will not be sharing anything except your usernames and the final product.')

            def check(m):
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

            try:
                confirm = await self.bot.wait_for('message', check=check, timeout=30)
                if confirm.content.lower() in ('yes',):
                    send = True
            except asyncio.TimeoutError:
                pass

        if send:
            ch = self.bot.get_channel(765759340405063680)
            if len(final_story) > 2042:
                final_story = final_story[:2041]
            embed = discord.Embed(
                title=template_name,
                description=f'```{final_story}```',
                color=discord.Colour.orange()
            )
            embed.add_field(name='Participants', value=', '.join(u.name for u in participants))
            await ch.send(embed=embed)

        s = 'Sent! ' if send else ''
        message = await ctx.send(f'{s}Grand finale in **3...**')
        await asyncio.sleep(1)
        await message.edit(content='Grand finale in **2...**')
        await asyncio.sleep(1)
        await message.edit(content='Grand finale in **1...**')
        await asyncio.sleep(1)
        await message.edit(content=f'**{template_name}**\nBy {", ".join([user.mention for user in participants])}')
        for page in pages:
            await ctx.send(page)

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

        query = 'SELECT creator_id FROM madlibs WHERE name = $1 AND guild_id = $2'
        creator_id = await self.bot.db.fetchrow(query, name, ctx.guild.id)

        if creator_id:
            creator_id = creator_id['creator_id']

            if ctx.author.id != creator_id and not ctx.author.guild_permissions.manage_guild:
                return await ctx.send('You are not authorized to delete this tag.')

            query = 'DELETE FROM madlibs WHERE name = $1 AND guild_id = $2'
            await self.bot.db.execute(query, name, ctx.guild.id)

            await ctx.send(f':thumbsup: Successfully deleted custom story template {name}.')
        else:
            await ctx.send(f':no_entry: No custom template with name `{name}` found.')

    @custom.command(name='edit')
    async def _edit(self, ctx, name, *, edited):

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
        query = 'SELECT name FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, ctx.guild.id)

        if not rows:
            return await ctx.send(f':no_entry: No custom templates found in this guild.')

        await ctx.send("**All Custom Templates:**\n\n" + '\n'.join(['`' + row['name'] + '`' for row in rows]))

    @custom.command(name='info')
    async def _info(self, ctx, *, name):

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
            embed.add_field(name='Creator', value=f'<@{row["plays"]}>\n(not in server)')
        else:
            embed.add_field(name='Creator', value=f'{user.mention}')
            embed.set_author(name=str(user), icon_url=str(user.avatar_url_as(format='png')))

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

    @commands.command()
    async def plays(self, ctx, index: int, *, storyname=None):

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
            story = rows[index - 1]
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
