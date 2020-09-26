from discord.ext import commands


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
        elif isinstance(error, self.bot.Blacklisted):
            return
        elif isinstance(error, commands.NotOwner):
            await ctx.send('\\\u274c This command is restricted for the owner.')
        elif isinstance(error, self.bot.CannotEmbedLinks):
            await ctx.send('\\\u274c I need the `Embed Links` permission to have all functionality!')
        elif isinstance(error, commands.MissingPermissions):
            missing_perms = ' '.join([word.capitalize() for word in error.missing_perms[0].split('_')])
            await ctx.send(f'\\\u274c '
                           f'You need the `{missing_perms}` permission to do `{ctx.prefix}{ctx.invoked_with}`.')
        else:
            raise error


def setup(bot):
    bot.add_cog(Listeners(bot))
