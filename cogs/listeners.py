from discord.ext import commands
import aiohttp
import time
from cogs.utils import humanize


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.on_ready())

    async def on_ready(self):
        await self.bot.wait_until_ready()
        print('Ready')
        self.bot.up_at = time.time()
        self.bot.session = aiohttp.ClientSession()

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
            await ctx.send(f':no_entry: This command is restricted for the owner.')
        elif isinstance(error, self.bot.CannotEmbedLinks):
            await ctx.send(f':no_entry: I need the `Embed Links` permission to have all functionality!')
        elif isinstance(error, commands.CommandOnCooldown):
            rate, per = error.cooldown.rate, error.cooldown.type
            s = '' if rate == 1 else 's'
            await ctx.send(f'You can only give feedback {rate} time{s} per {humanize(per)}. Please wait another '
                           f'`{error.retry_after:.2f}` seconds.')
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(f':no_entry: There is already a game taking place in this channel.')
        elif isinstance(error, commands.MissingPermissions):
            missing_perms = ' '.join([word.capitalize() for word in error.missing_perms[0].split('_')])
            await ctx.send(f':no_entry: '
                           f'You need the `{missing_perms}` permission to do `{ctx.prefix}{ctx.invoked_with}`.')
        else:
            raise error


def setup(bot):
    bot.add_cog(Listeners(bot))
