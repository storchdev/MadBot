from discord.ext import commands, menus
import discord
import time
import asyncio
import re
import json


finder = re.compile('{.+?}')
cross_mark = '\U0000274c'

with open('./defaults.json') as f:
    lengths = {}
    defaults = json.load(f)

    for default in defaults.keys():
        length = len(finder.findall(defaults[default]))
        lengths[default] = length


def create_embed(page, is_custom, rows=None):
    paginator = commands.Paginator(max_size=500, prefix='', suffix='')
    i = 1

    embed = discord.Embed(color=discord.Colour.blue())
    embed.set_footer(text=f'\U000026ab - Custom Templates\n\U000026aa - Default Templates')

    if not is_custom:

        for template in defaults.keys():
            line = f'`{i}.` **{template}** ({defaults.lengths[template]} blanks)'
            paginator.add_line(line)
            i += 1
        pages = paginator.pages
        embed.set_author(name=f'Page {page}/{len(pages)}')
        embed.title = f'{len(defaults.defaults)} Default Templates'
        embed.description = pages[page - 1]

    else:
        embed = discord.Embed(color=discord.Colour.blue())
        embed.title = f'{len(rows)} Custom Templates'
        embed.set_footer(text=f'\U000026ab - Custom Templates\n\U000026aa - Default Templates')

        if rows:
            for row in rows:
                blanks = len(defaults.finder.findall(row[1]))
                line = f'`{i}.` **{row[0]}** ({blanks} blanks)'
                paginator.add_line(line)
                i += 1

            pages = paginator.pages
            embed.description = pages[page - 1]
            embed.set_author(name=f'Page {page}/{len(pages)}')
        else:
            embed.description = 'No custom templates found.'
            embed.set_author(name='Page 0')
            return embed, 0

    return embed, len(pages)


class Templates(menus.Menu):

    def __init__(self, *, timeout=180.0, delete_message_after=False,
                 clear_reactions_after=True, check_embeds=False, message=None):
        super().__init__(timeout=180.0, delete_message_after=False, clear_reactions_after=True, check_embeds=False,
                         message=None)
        self.page = 1
        self.max_length = 1
        self.on_custom = False
        self.rows = []

    async def send_initial_message(self, ctx, channel):
        embed, self.max_length = create_embed(1, False)

        async with self.bot.db.cursor() as cur:
            await cur.execute('SELECT name, template FROM madlibs WHERE guild_id = ?', (ctx.guild.id,))
            rows = await cur.fetchall()
            self.rows = rows

        return await channel.send(embed=embed)

    @menus.button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_first(self, payload):

        if self.on_custom:
            embed = create_embed(1, True, self.rows)[0]
        else:
            embed = create_embed(1, False)[0]

        self.page = 1
        await self.message.edit(embed=embed)

    @menus.button('\N{BLACK LEFT-POINTING TRIANGLE}')
    async def on_left(self, payload):

        if self.page > 1:
            self.page -= 1

            if self.on_custom:
                embed = create_embed(self.page, True, self.rows)[0]
            else:
                embed = create_embed(self.page, False)[0]

            await self.message.edit(embed=embed)

    @menus.button('\N{BLACK RIGHT-POINTING TRIANGLE}')
    async def on_right(self, payload):

        if self.page < self.max_length:
            self.page += 1

            if self.on_custom:
                embed = create_embed(self.page, True, self.rows)[0]
            else:
                embed = create_embed(self.page, False)[0]

            await self.message.edit(embed=embed)

    @menus.button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def on_last(self, payload):

        if self.page != self.max_length:
            self.page = self.max_length

            if self.on_custom:
                embed = create_embed(self.page, True, self.rows)[0]
            else:
                embed = create_embed(self.page, False)[0]

            await self.message.edit(embed=embed)

    @menus.button('\N{MEDIUM BLACK CIRCLE}')
    async def on_jump_to_custom(self, payload):

        if not self.on_custom:
            self.on_custom = True
            self.page = 1

            embed = create_embed(self.page, True, self.rows)[0]
            await self.message.edit(embed=embed)

    @menus.button('\N{MEDIUM WHITE CIRCLE}')
    async def on_jump_to_default(self, payload):

        if self.on_custom:
            self.on_custom = False
            self.page = 1

            embed = create_embed(self.page, False)[0]
            await self.message.edit(embed=embed)


class MadLibs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.in_game = []
        self.finder = finder
        self.cross_mark = '\U0000274c'
        self.defaults = defaults
        self.lengths = lengths

        i = 1
        templates = {}
        for name in self.defaults.keys():
            templates[i] = {
                "name": name,
                "template": self.defaults[name],
                "blanks": self.lengths[name],
                "is_custom": False
            }
            i += 1

    @commands.command()
    async def madlibs(self, ctx):

        if ctx.channel.id in self.in_game:
            return await ctx.send(f'{self.cross_mark} There is already a game taking place in this channel.')
        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(f'{self.cross_mark} I need the `Embed Links` permission start a game.')

        self.in_game.append(ctx.channel.id)

        participants = [ctx.author]
        embed = discord.Embed(color=discord.Colour.green())
        embed.title = 'A MadLibs game is starting in this channel!'
        embed.description = f'Send `join` in chat to join!'
        embed.set_footer(text='If you are the host, please send [start] to start the game.')
        await ctx.send(embed=embed)

        timeout_in = 30
        end = time.time() + timeout_in

        def check(m):
            return m.channel.id == ctx.channel.id and (m.content.lower() == 'join' and m.author.id != ctx.author.id or
                                                       m.content.lower() == 'start' and m.author.id == ctx.author.id)

        while True:

            try:
                message = await self.bot.wait_for('message', check=check, timeout=end - time.time())

                if message.author.id == ctx.author.id:
                    break
                else:
                    participants.append(message.author)

            except asyncio.TimeoutError:
                break

        await Templates().start(ctx)

    @commands.group(invoke_without_command=True)
    async def custom(self, ctx):
        await ctx.send(f'''To **add** a custom template, do this: ```
{ctx.prefix}custom add "<name>" <template>```
Surround the name of blanks with curly brackets {{}}
Example: `{ctx.prefix}custom add "example" The {{noun}} is {{adjective}}`.

To **edit** a custom template, do this: ```
{ctx.prefix}custom edit <name> <new version>```
To **delete** a custom template, do this: ```
{ctx.prefix}custom delete <name>```
To **get info** on a custom template, do this: ```
{ctx.prefix}custom info <name>```
To **list all** custom templates, do this: ```
{ctx.prefix}custom all```''')

    @custom.command(name='add', aliases=['create'])
    async def _add(self, ctx, name, *, template):
        name = name.strip(' ')
        template = template.strip(' ')

        if not len(finder.findall(template)):
            return await ctx.send('Make sure to include **at least one blank** in the template. Blanks are '
                                  'placeholders marked with curly brackets, like `{noun}`.')

        async with self.bot.db.cursor() as cur:
            query = 'SELECT id FROM madlibs WHERE name = ? AND guild_id = ?'
            await cur.execute(query, (name, ctx.guild.id))
            exists = await cur.fetchone()

            if exists:
                return await ctx.send(f'{self.cross_mark} '
                                      f'A custom template with name `{name}` already exists in this guild.')

            query = 'INSERT INTO madlibs (name, template, guild_id, creator_id, plays) VALUES (?, ?, ?, ?, ?)'
            await cur.execute(query, (name, template, ctx.guild.id, ctx.author.id, 0))
            await self.bot.db.commit()
            await ctx.send(f'Successfully added custom story template with name `{name}`!')

    @custom.command(name='delete', aliases=['remove', 'nize'])
    async def _delete(self, ctx, *, name):

        async with self.bot.db.cursor() as cur:
            query = 'SELECT creator_id FROM madlibs WHERE name = ? AND guild_id = ?'
            await cur.execute(query, (name, ctx.guild.id))
            exists = await cur.fetchone()

            if exists:
                creator_id = exists[0]

                if ctx.author.id != creator_id and not ctx.author.guild_permissions.manage_guild:
                    return await ctx.send('You are not authorized to delete this tag.')

                query = 'DELETE FROM madlibs WHERE name = ? AND guild_id = ?'
                await cur.execute(query, (name, ctx.guild.id))
                await self.bot.db.commit()
            else:
                await ctx.send(f'{self.cross_mark} No custom template with name `{name}` found.')

    @custom.command(name='edit')
    async def _edit(self, ctx, name, *, edited):

        async with self.bot.db.cursor() as cur:
            query = 'SELECT creator_id FROM madlibs WHERE name = ? AND guild_id = ?'
            await cur.execute(query, (name, ctx.guild.id))
            exists = await cur.fetchone()

            if not exists:
                return await ctx.send(f'{self.cross_mark} No custom template with name `{name}` found.')

            creator_id = exists[0]

            if ctx.author.id != creator_id and not ctx.author.guild_permissions.manage_guild:
                return await ctx.send(f'{self.cross_mark} You are not authorized to edit this tag.')

            query = 'UPDATE madlibs SET template = ? WHERE name = ? AND guild_id = ?'
            await cur.execute(query, (edited, name, ctx.guild.id))
            await self.bot.db.commit()

    @custom.command(name='all')
    async def _all(self, ctx):

        async with self.bot.db.cursor() as cur:
            query = 'SELECT name FROM madlibs WHERE guild_id = ?'
            await cur.execute(query, (ctx.guild.id,))
            rows = await cur.fetchall()

            if not rows:
                return await ctx.send(f'{self.cross_mark} No custom templates found in this guild.')

            await ctx.send("**All Custom Templates:**\n\n" + ' '.join(['`' + row[0] + '`' for row in rows]))

    @custom.command(name='info')
    async def _info(self, ctx, *, name):

        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(f'{self.cross_mark} I need the `Embed Links` permission to send info.')

        async with self.bot.db.cursor() as cur:
            query = 'SELECT template, creator_id, plays FROM madlibs WHERE guild_id = ? AND name = ?'
            await cur.execute(query, (ctx.guild.id, name))
            row = await cur.fetchone()

            if not row:
                return await ctx.send(f'{self.cross_mark} No template called `{name}` was found.')

            embed = discord.Embed(color=discord.Colour.blue())
            embed.title = name
            embed.add_field(name='Number of Plays', value=f'**{row[2]}**')

            user = ctx.guild.get_member(row[1])
            if not user:
                embed.add_field(name='Creator', value=f'<@{row[2]}>\n(left guild)')
            else:
                embed.add_field(name='Creator', value=f'{user.mention}')
                embed.set_author(name=str(user), icon_url=str(user.avatar_url_as(format='png')))

            blanks = finder.findall(row[0])
            embed.add_field(name='Number of Blanks', value=f'**{len(blanks)}**')

            blanks = ', '.join([word.lstrip('{').rstrip('}') for word in blanks])

            if len(blanks) <= 1024:
                embed.add_field(name='Blanks', value=blanks)

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MadLibs(bot))
