from discord.ext import commands 


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            missing_perms = ' '.join([word.capitalize() for word in error.missing_perms[0].split('_')])
            await ctx.send(f'You need the `{missing_perms}` to do the `{ctx.prefix}{ctx.invoked_with}`.')
        
def setup(bot):
    bot.add_cog(Listeners(bot))
