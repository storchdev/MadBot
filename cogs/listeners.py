from discord.ext import commands
import aiohttp
import time
from humanize import precisedelta


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.on_ready())
        self.support_id = 765757769575038986
        self.supporter_role_id = 765764229104926741

    async def on_ready(self):
        await self.bot.wait_until_ready()
        print('Ready')
        self.bot.up_at = time.time()
        self.bot.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.bot.session.close())

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await (await self.bot.fetch_user(718475543061987329)).send(f'i have joined {guild.name}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, self.bot.Blacklisted):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            usage = ctx.command.help.split('|')[1]
            usage = f'{ctx.clean_prefix}{ctx.command.name} {usage}'
            await ctx.send(f':no_entry: The correct usage is: `{usage}`')
        elif isinstance(error, commands.NotOwner):
            await ctx.send(f':no_entry: This command is restricted for the owner.')
        elif isinstance(error, self.bot.CannotEmbedLinks):
            await ctx.send(f':no_entry: I need the `Embed Links` permission to have all functionality!')
        elif isinstance(error, commands.CommandOnCooldown):
            rate, per = error.cooldown.rate, error.cooldown.per
            s = '' if rate == 1 else 's'
            await ctx.send(f':no_entry: You can only use this command {rate} time{s} every {precisedelta(per)}. '
                           f'Please wait another `{error.retry_after:.2f}` seconds.')
        elif isinstance(error, commands.MissingPermissions):
            missing_perms = ' '.join([word.capitalize() for word in error.missing_permissions[0].split('_')])
            await ctx.send(f':no_entry: '
                           f'You need the `{missing_perms}` permission to do `{ctx.prefix}{ctx.invoked_with}`.')
        else:
            raise error


def setup(bot):
    bot.add_cog(Listeners(bot))
