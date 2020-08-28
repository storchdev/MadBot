from discord.ext import commands 
import json
from datetime import datetime


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.query = 'INSERT INTO messages (message_id, author_id, channel_id, guild_id, content, timestamp, ' \
                     'is_bot, attachments, embeds) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)'

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.get_user(553058885418876928).send(f'i have joined {guild.name}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            missing_perms = ' '.join([word.capitalize() for word in error.missing_perms[0].split('_')])
            await ctx.send(f'You need the `{missing_perms}` to do the `{ctx.prefix}{ctx.invoked_with}`.')

        if ctx.command.name == 'add':
            await ctx.send('You must provide both a **name** and a **story** for your custom template.')
        elif ctx.command.name == 'delete':
            await ctx.send('You must provide the **name** of the template to delete.')
        elif ctx.command.name == 'edit':
            await ctx.send('You must provide both the **name** of the template to edit and the **new edited version**.')
        elif ctx.command.name == 'info':
            await ctx.send(f'You must provide the **name** of the template to get info on.')

    @commands.Cog.listener()
    async def on_message(self, message):

        embeds = json.dumps([embed.to_dict() for embed in message.embeds], indent=4)
        attachments = json.dumps([attachment.url for attachment in message.attachments])
        guild_id = 0 if not message.guild else message.guild.id

        await self.bot.execute(self.query, (
            message.id,
            message.author.id,
            message.channel.id,
            guild_id,
            message.content,
            int(datetime.timestamp(message.created_at)),
            message.author.bot,
            attachments,
            embeds
        ))

        if not message.guild or message.author.bot:
            return


def setup(bot):
    bot.add_cog(Listeners(bot))
