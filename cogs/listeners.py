from discord.ext import commands
import json
from datetime import datetime


query = 'INSERT INTO messages (message_id, author_id, channel_id, guild_id, content, timestamp, ' \
        'is_bot, attachments, embeds, is_edited, is_deleted) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)'


async def insert_message(bot, message):
    embeds = json.dumps([embed.to_dict() for embed in message.embeds], indent=4)
    attachments = json.dumps([attachment.url for attachment in message.attachments], indent=4)
    guild_id = 0 if not message.guild else message.guild.id
    args = (
        message.id,
        message.author.id,
        message.channel.id,
        guild_id,
        message.content,
        int(datetime.timestamp(message.created_at)),
        message.author.bot,
        attachments,
        embeds,
        False,
        False
    )
    await bot.db.execute(query, *args)


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.delete_query = 'UPDATE messages SET is_deleted = $1 WHERE message_id = $2'
        self.edit_query = 'UPDATE messages SET is_edited = $1 WHERE message_id = $2'
        self.member_query = 'INSERT INTO member_logs (member_id, roles, nickname) VALUES ($1, $2, $3)'
        self.user_query = 'INSERT INTO user_logs (user_id, username) VALUES ($1, $2)'

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.get_user(553058885418876928).send(f'i have joined {guild.name}')

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #
    #     if isinstance(error, commands.CommandNotFound):
    #         return
    #     elif isinstance(error, commands.MissingPermissions):
    #         missing_perms = ' '.join([word.capitalize() for word in error.missing_perms[0].split('_')])
    #         await ctx.send(f'You need the `{missing_perms}` to do the `{ctx.prefix}{ctx.invoked_with}`.')
    #
    #     if ctx.command.name == 'add':
    #         await ctx.send('You must provide both a **name** and a **story** for your custom template.')
    #     elif ctx.command.name == 'delete':
    #         await ctx.send('You must provide the **name** of the template to delete.')
    #     elif ctx.command.name == 'edit':
    #         await ctx.send('You must provide both the **name** of the template to edit and the **new edited version**.')
    #     elif ctx.command.name == 'info':
    #         await ctx.send(f'You must provide the **name** of the template to get info on.')

    @commands.Cog.listener()
    async def on_message(self, message):
        await insert_message(self.bot, message)
        if not message.guild or message.author.bot:
            return

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        await self.bot.db.execute(self.edit_query, True, payload.message_id)
        await insert_message(self.bot, message)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        await self.bot.db.execute(self.delete_query, True, payload.message_id)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        q = self.delete_query
        for message_id in payload.message_ids:
            await self.bot.db.execute(q, True, message_id)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles or before.display_name != after.display_name:
            roles = json.dumps([role.id for role in after.roles], indent=4)
            nickname = after.display_name
            await self.bot.db.execute(self.member_query, after.id, roles, nickname)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            await self.bot.db.execute(self.user_query, after.id, after.name)


def setup(bot):
    bot.add_cog(Listeners(bot))
