from discord.ext import commands
from discord import app_commands
import discord
import time
import asyncio
from cogs.menus import TemplatesMenu, YesNo, ViewMenu
from cogs.utils import capitalize, placeholder, vowel
from cogs.dicts import pos_dict, defaults_dict
import json
import typing


def generate_embeds(names, templates, *, default=True):
    if default:
        title = 'Default Templates'
    else:
        title = 'Custom Templates'

    indices = {0: {}}
    i = 1
    pages_len = 0

    pages = []
    page = ''

    for name, template in zip(names, templates):
        length = len(placeholder.findall(template))
        line = f'`{i}.` **{name}** ({length} blanks)\n'
        indices[pages_len][i] = (name, template)
        page += line

        if len(page) + len(line) > 500:
            pages.append(page)
            page = ''
            pages_len += 1
            indices[pages_len] = {}

        i += 1

    if page:
        pages.append(page)

    i = 1

    embeds = []
    for page in pages:
        embed = discord.Embed(
            title=f'{title} - Page {i}/{len(pages)}',
            color=discord.Colour.blurple(),
            description=page
        )
        embeds.append(embed)
        i += 1

    return embeds, indices


current_games = []


class Game:
    def __init__(self, interaction, main_view, task):
        self.interaction = interaction
        self.main_view = main_view
        self.task = task
        self.bot = self.interaction.client
        self.story_view = None
        self.channel_id = self.interaction.channel.id

    async def create_story_view(self):
        defaults, defaults_i = generate_embeds(defaults_dict.keys(), defaults_dict.values())

        query = 'SELECT name, template FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, self.interaction.guild.id)
        customs, customs_i = generate_embeds(
            [row['name'] for row in rows],
            [row['template'] for row in rows],
            default=False
        )

        self.story_view = TemplatesMenu(self.interaction, defaults, customs, defaults_i, customs_i)
        self.story_view.message = await self.interaction.followup.send(embed=defaults[0], view=self.story_view)
        return self.story_view

    async def cancel(self):
        if self in current_games:
            current_games.remove(self)
        self.main_view.clear_items()
        await self.main_view.message.edit(view=self.main_view)

async def madlibs_check(interaction):
    bot = interaction.client
    query = 'SELECT max_games FROM settings WHERE guild_id = $1'
    row = await bot.db.fetchrow(query, interaction.guild.id)
    
    if row is None:
        limit = 1 
    else:
        limit = row['max_games']
    num_games = len([game for game in current_games if game.channel_id == interaction.channel.id])
    if num_games >= limit:
        await interaction.response.send_message(
            f':no_entry: There is a limit of `{limit}` concurrent games per channel. An admin can override this setting.',
            ephemeral=True
        )
        return False 

    return True
    
class MadLibs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.speech = pos_dict

    @app_commands.command()
    @app_commands.check(madlibs_check)
    async def madlibs(self, interaction):
        """Starts a Mad Libs game with you as the host."""

        query = 'SELECT max_players, time_limit FROM settings WHERE guild_id = $1'
        row = await self.bot.db.fetchrow(query, interaction.guild.id)
        if row is None:
            max_players = 10 
            time_limit = 45
        else:
            max_players = row['max_players']
            time_limit = row['time_limit']

        participants = [interaction.user]
        game = None
        started = False

        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label='Join!', style=discord.ButtonStyle.green)
        button2 = discord.ui.Button(label='Leave', style=discord.ButtonStyle.blurple)
        button3 = discord.ui.Button(label='Start!', style=discord.ButtonStyle.blurple, row=2)
        button4 = discord.ui.Button(label='Cancel', style=discord.ButtonStyle.red, row=2)

        async def start():
            story_view = await game.create_story_view()
            await story_view.wait()
            name, template = story_view.name, story_view.template

            if not name:
                await game.cancel()
                await story_view.message.edit(
                    f':alarm_clock: You spent too long selecting a story. Game canceled.',
                    embed=None, view=None
                )
                return

            blanks = placeholder.findall(template)

            progress = 1
            total = len(blanks)
            while True:
                blank = blanks[progress - 1]

                try:
                    user = participants[0]
                except IndexError:
                    await game.cancel()
                    return await interaction.channel.send(f':warning: Game was abandoned by all players.')

                n = 'n' if vowel.match(blank) else ''
                hint = ' (NOT ENDING IN "ING")' if blank.lower() == 'verb' else ''

                dots = discord.ui.View(timeout=time_limit)
                dots_btn = discord.ui.Button(label='\U0001f4ac', style=discord.ButtonStyle.blurple)
                received = None

                async def callback(word_i):
                    ref = {
                        'noun': 'A THING',
                        'proper noun': 'A PERSON OR PLACE',
                        'verb': 'A PLAIN ACTION',
                        'verb ending in ING': 'AN ACTION ENDING IN "ING"',
                        'verb (past tense)': 'AN ACTION THAT HAPPEN[ED] IN THE PAST',
                        'adjective': 'A DESCRIBING WORD',
                        'adverb': 'A WORD ENDING IN "LY"'
                    }
                    if word_i.user != user:
                        return await word_i.response.defer()
                    if blank.lower() in ref:
                        ref = ref[blank.lower()]
                    else:
                        ref = '\u200b'

                    class Modal(discord.ui.Modal, title=f'Enter a{n} {blank}.'):

                        word = discord.ui.TextInput(label=ref, max_length=69, style=discord.TextStyle.short)

                        async def on_submit(self, modal_i):
                            nonlocal received
                            if dots.is_finished():
                                await modal_i.response.send_message(
                                    ':no_entry: You were kicked from the game before submitting your word. '
                                    'You may rejoin at any time.',
                                    ephemeral=True
                                )
                                return

                            received = str(self.word)
                            dots.stop()
                            await modal_i.response.send_message(
                                f':thumbsup: {modal_i.user.mention} entered `{received}`'
                            )

                    modal = Modal()
                    await word_i.response.send_modal(modal)

                dots_btn.callback = callback
                dots.add_item(dots_btn)
                message = await interaction.channel.send(
                    f'{user.mention}, press the button to enter a{n} **{blank}{hint}**. ({progress}/{total})',
                    view=dots
                )

                await dots.wait()
                await message.delete()

                if received:
                    participants.pop(0)
                    participants.append(user)

                    template = template.replace(f'{{{blank}}}', received, 1)
                    if progress == total:
                        break
                    progress += 1
                else:
                    participants.remove(user)
                    await interaction.channel.send(
                        f':wave: \u23f0 {user.mention} has been removed from the game due to inactivity.'
                    )

            await game.cancel()
            pids = [p.id for p in participants]

            query = 'UPDATE madlibs SET plays = plays + 1 WHERE guild_id = $1 AND name = $2'
            await self.bot.db.execute(query, interaction.guild.id, name)
            query = 'INSERT INTO plays (channel_id, participants, final_story, played_at, name, guild_id) ' \
                    'VALUES ($1, $2, $3, $4, $5, $6)'
            await self.bot.db.execute(
                query,
                interaction.channel.id,
                json.dumps(pids, indent=4),
                template,
                int(time.time()),
                name,
                interaction.guild.id
            )

            embedded_story = ''
            pages = []
            final_story = capitalize(template)

            for word in final_story.split():
                word += ' '

                if len(word + embedded_story) > 2048:
                    pages.append(embedded_story)
                    embedded_story = ''
                else:
                    embedded_story += word
            pages.append(embedded_story)

            if interaction.user.id in pids:
                yesno = YesNo(interaction, name, final_story, participants)
                yesno.message = await interaction.channel.send(
                    f'{interaction.user.mention}, would you like to send this result to my support server? '
                    'I will not be sharing anything except your usernames and the final product.',
                    view=yesno
                )
                await yesno.wait()

            i = 3
            message = await interaction.channel.send(f':tada: Grand finale in **3...** :tada:')
            while i > 0:
                i -= 1
                await asyncio.sleep(1)
                await message.edit(content=f':tada: Grand finale in **{i}...** :tada:')

            await asyncio.sleep(1)
            i = 0
            names = ", ".join([user.display_name for user in participants])
            for page in pages:
                embed = discord.Embed(description=page, color=interaction.user.color)
                embed.set_footer(text='By ' + names)
                if i == 0:
                    embed.title = name
                await message.edit(content=None, embed=embed)
                i += 1

        async def join_callback(join_i):
            u = join_i.user
            if u not in participants:
                if len(participants) >= max_players:
                    return await join_i.response.send_message(
                        f':no_entry: Sorry, there is a limit of {max_players} players per game!',
                        ephemeral=True
                    )
                participants.append(u)
                await join_i.response.send_message(f':wave: {u.mention} has joined the game!')
            else:
                await join_i.response.send_message(
                    f':no_entry: You are already in the game.',
                    ephemeral=True
                )

        async def leave_callback(leave_i):
            u = leave_i.user
            if u not in participants:
                return await interaction.response.defer()

            if u == interaction.user:
                return await leave_i.response.send_message(
                    f':no_entry: Hosts cannot leave the game.',
                    ephemeral=True
                )

            participants.remove(u)
            await leave_i.response.send_message(f':wave: {u.mention} has left the game.')

        async def start_callback(start_i):
            nonlocal started

            u = start_i.user
            if u != interaction.user:
                return await interaction.response.defer()

            started = True
            view.remove_item(button3)
            await view.message.edit(view=view)
            await start_i.response.send_message(
                ':thumbsup: Let\'s do this! Please choose a story now.',
                ephemeral=True
            )

            task = self.bot.loop.create_task(start())
            game.task = task

        async def cancel_callback(cancel_i):
            u = cancel_i.user
            if u != interaction.user:
                return await interaction.response.defer()
            await game.cancel()
            if game.task:
                game.task.cancel()

            await cancel_i.response.send_message(':octagonal_sign: Game canceled.', ephemeral=True)

        button.callback = join_callback
        button2.callback = leave_callback
        button3.callback = start_callback
        button4.callback = cancel_callback

        for b in [button, button2, button3, button4]:
            view.add_item(b)

        embed = discord.Embed(
            title='A MadLibs game is starting!',
            description='Click the green `Join` button to join in on the fun.',
            color=discord.Colour.green()
        )
        await interaction.response.send_message(
            'Other players have 5 minutes to join. Press the `Start` button when you are ready.',
            ephemeral=True
        )

        view.message = await interaction.channel.send(embed=embed, view=view)
        game = Game(interaction, view, task=None)
        current_games.append(game)

        await asyncio.sleep(300)
        if not started:
            if game not in current_games:
                return 
                
            await game.cancel()
            await interaction.followup.send(
                f':alarm_clock: {interaction.user.mention}\n'
                f'5 minutes have passed and you have not started the game, so I have canceled it.'
            )

    @app_commands.command()
    @app_commands.describe(storyname='The name of the template that was played')
    async def history(self, interaction, storyname: str = None):
        """Allows you to view all past games that have occured in this server."""

        if storyname:
            query = 'SELECT channel_id, participants, final_story, played_at, name FROM plays ' \
                    'WHERE guild_id = $1 AND name = $2'
            rows = await self.bot.db.fetch(query, interaction.guild.id, storyname)
        else:
            query = 'SELECT channel_id, participants, final_story, played_at, name FROM plays ' \
                    'WHERE guild_id = $1'
            rows = await self.bot.db.fetch(query, interaction.guild.id)

        if not rows:
            return await interaction.response.send_message(':no_entry: No past games found.')

        embeds = []

        for story in rows:

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

            embed.add_field(name='Played At', value=f'<t:{story["played_at"]}:R>')

            embeds.append(embed)

        view = ViewMenu(interaction, embeds, timeout=None)
        view.message = await interaction.response.send_message(embed=embeds[0], view=view)

    @app_commands.command()
    @app_commands.describe(part='The part of speech to lookup')
    async def pos(self, interaction, part: typing.Literal["noun", "adjective", "verb", "adverb"]):
        """Gives information on the main parts of speech"""
        await interaction.response.send_message(self.speech[part])


async def setup(bot):
    await bot.add_cog(MadLibs(bot))
