import dbl
from discord.ext import commands, tasks
from config import TOPGG_API_TOKEN
import datetime
import discord
from discord import app_commands


class TopGG(commands.Cog, name='top.gg', description='Nothing much here. Just vote if you want.'):

    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.DBLClient(self.bot, TOPGG_API_TOKEN, autopost=True)

    @app_commands.command()
    async def vote(self, inter):
        """Sends the link to vote for the bot."""

        await inter.response.send_message('https://top.gg/bot/742921922370600991/vote\n\n**Thanks for your support!**')

    @tasks.loop(hours=1)
    async def post_guild_count(self):
        await self.dblpy.post_guild_count(len(self.bot.guilds))
        print(f'Posted guild count to top.gg at {datetime.datetime.now().astimezone().strftime("%c")}')

    @post_guild_count.before_loop
    async def wait_until_hour(self):
        now = datetime.datetime.now().astimezone()
        next_run = now.replace(minute=0, second=0)

        if next_run < now:
            next_run += datetime.timedelta(hours=1)

        await discord.utils.sleep_until(next_run)


def setup(bot):
    bot.add_cog(TopGG(bot))
