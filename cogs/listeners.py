from discord.ext import commands 


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')

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

        if not message.guild or message.author.bot:
            return


def setup(bot):
    bot.add_cog(Listeners(bot))
