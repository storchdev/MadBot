from discord import app_commands as slash
import discord
from discord.ext import commands
import time
from cogs.utils import placeholder


class Custom(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    group = slash.Group(name='custom', description='Lets you manage custom-made templates in this server.')

    @group.command(name='add')
    async def custom_add(self, interaction):
        """Adds a new custom story template to the server."""

        class Modal(discord.ui.Modal, title='Make a Cool Story'):
            name = discord.ui.TextInput(label='Name of your story', max_length=32)
            template = discord.ui.TextInput(label='Your story\'s template goes here', style=discord.TextStyle.long)

            async def on_submit(self, modal_inter):
                bot = modal_inter.client

                name = str(self.name)
                template = str(self.template)

                if not len(placeholder.findall(template)):
                    return await modal_inter.response.send_message(
                        f':no_entry: Make sure to include **at least one blank** in the template. '
                        'Blanks are placeholders marked with curly brackets, like `{noun}`.',
                        ephemeral=True
                    )

                query = 'SELECT id FROM madlibs WHERE name = $1 AND guild_id = $2'
                exists = await bot.db.fetchrow(query, name, interaction.guild.id)

                if exists:
                    return await modal_inter.response.send_message(
                        f':no_entry: A custom template with name `{name}` already exists in this guild.',
                        ephemeral=True
                    )

                query = 'INSERT INTO madlibs (name, template, guild_id, creator_id, plays, created_at) ' \
                        'VALUES ($1, $2, $3, $4, $5, $6)'
                await bot.db.execute(
                    query,
                    name,
                    template,
                    interaction.guild.id,
                    interaction.user.id,
                    0,
                    int(time.time())
                )
                await modal_inter.response.send_message(
                    f':thumbsup: Successfully added custom story template with name `{name}`!',
                    ephemeral=True
                )

        await interaction.response.send_modal(Modal())

    @group.command(name='delete')
    @slash.describe(name='The name of the story to delete')
    async def custom_delete(self, interaction, name: str):
        """Deletes an existing custom template from the server."""

        query = 'SELECT creator_id FROM madlibs WHERE name = $1 AND guild_id = $2'
        creator_id = await self.bot.db.fetchrow(query, name, interaction.guild.id)

        if not creator_id:
            return await interaction.response.send_message(
                f':no_entry: No custom template with name `{name}` found.',
                ephemeral=True
            )

        creator_id = creator_id['creator_id']

        if interaction.user.id != creator_id and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                ':no_entry: You are not authorized to delete this tag.',
                ephemeral=True
            )

        query = 'DELETE FROM madlibs WHERE name = $1 AND guild_id = $2'
        await self.bot.db.execute(query, name, interaction.guild.id)

        await interaction.response.send_message(
            f':thumbsup: Successfully deleted custom story template `{name}`.',
            ephemeral=True
        )

    @group.command(name='edit')
    @slash.describe(
        name='The name of the story to edit'
    )
    async def custom_edit(self, interaction, name: str):
        """Edits an existing custom template."""

        query = 'SELECT creator_id FROM madlibs WHERE name = $1 AND guild_id = $2'
        creator_id = await self.bot.db.fetchrow(query, name, interaction.guild.id)

        if not creator_id:
            return await interaction.response.send_message(
                f':no_entry: No custom template with name `{name}` found.',
                ephemeral=True
            )

        creator_id = creator_id['creator_id']

        if interaction.user.id != creator_id and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                f':no_entry: You are not authorized to edit this template.',
                ephemeral=True
            )

        class Modal(discord.ui.Modal, title=f'Edit a Cool Story'):
            edited = discord.ui.TextInput(label=f'New version of your story goes here', style=discord.TextStyle.long)

            async def on_submit(self, modal_inter):
                bot = modal_inter.client
                edited = str(self.edited)

                if not len(placeholder.findall(edited)):
                    return await modal_inter.response.send_message(
                        f':no_entry: Make sure to include **at least one blank** in the template. '
                        'Blanks are placeholders marked with curly brackets, like `{noun}`.',
                        ephemeral=True
                    )

                query = 'UPDATE madlibs SET template = $1 WHERE name = $2 AND guild_id = $3'
                await bot.db.execute(query, edited, name, interaction.guild.id)
                await modal_inter.response.send_message(
                    f':thumbsup: Successfully edited custom story template `{name}`.',
                    ephemeral=True
                )

        await interaction.response.send_modal(Modal())

    @group.command(name='list')
    async def custom_list(self, interaction):
        """Lists all the custom templates in the server."""

        query = 'SELECT name FROM madlibs WHERE guild_id = $1'
        rows = await self.bot.db.fetch(query, interaction.guild.id)

        if not rows:
            return await interaction.response.send_message(f':no_entry: No custom templates found in this guild.')

        i = 1
        text = ''
        for row in rows:
            line = f'**{i}.** {row["name"]}\n'
            if len(text + line) > 2048:
                break
            text += line
            i += 1

        embed = discord.Embed(
            title=f'User-Created Stories in {interaction.guild.name}',
            color=interaction.user.color,
            description=text
        ).set_footer(
            text=f'Do "/custom info" to see more details on a particular one'
        )
        await interaction.response.send_message(
            embed=embed
        )

    @group.command(name='info')
    @slash.describe(name='The name of the story to lookup')
    async def custom_info(self, interaction, name: str):
        """Gets info on a custom template."""

        if not interaction.channel.permissions_for(interaction.guild.me).embed_links:
            return await interaction.response.send_message(
                f':no_entry: I need the `Embed Links` permission to send info.',
                ephemeral=True
            )

        query = 'SELECT template, creator_id, plays, created_at FROM madlibs WHERE guild_id = $1 AND name = $2'
        row = await self.bot.db.fetchrow(query, interaction.guild.id, name)

        if not row:
            return await interaction.response.send_message(
                f':no_entry: No template called `{name}` was found.',
                ephemeral=True
            )

        embed = discord.Embed(
            title=name,
            color=discord.Colour.blue()
        )
        embed.add_field(name='Games Played', value=f'**{row["plays"]}**')
        embed.add_field(name='Creator', value=f'<@{row["creator_id"]}>')

        blanks = placeholder.findall(row['template'])

        if row['created_at']:
            embed.add_field(name='Created', value=f'<t:{row["created_at"]}:R>')

        if len(blanks) <= 1024:
            embed.add_field(name=f'Blanks ({len(blanks)})', value=', '.join(blanks))

        await interaction.response.send_message(embed=embed)

    @group.command(name='import')
    @slash.describe(
        guild_id='The ID of the server to import the story from',
        name='The name of the copied story in this server'
    )
    async def custom_import(self, interaction, guild_id: int, name: str):
        """Imports a custom template from another server. You will be the owner of it in this server."""

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await interaction.response.send_message(
                f':no_entry: Could not find server with ID `{guild_id}`.',
                ephemeral=True
            )

        query = 'SELECT template FROM madlibs WHERE guild_id = $1 AND name = $2'
        row = await self.bot.db.fetchrow(query, guild_id, name)
        if not row:
            return await interaction.response.send_message(
                f":no_entry: The template with name `{name}` doesn't exist in that server.",
                ephemeral=True
            )

        template = row['template']
        row = await self.bot.db.fetchrow(query, interaction.guild.id, name)
        if row:
            return await interaction.response.send_message(
                f':no_entry: A template with the name `{name}` already exists.',
                ephemeral=True
            )

        query = 'INSERT INTO madlibs (name, template, guild_id, creator_id, plays, created_at) ' \
                'VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(query, name, template, interaction.guild.id, interaction.user.id, 0, int(time.time()))
        await interaction.response.send_message(
            f':thumbsup: Successfully imported **{name}** from `{guild.name}`!',
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Custom(bot))
