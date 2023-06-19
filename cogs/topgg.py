from discord.ext import commands, tasks
import topgg
from config import TOPGG_API_TOKEN
import datetime
import discord


class TopGG(commands.Cog, name='top.gg', description='Nothing much here. Just vote if you want.'):

    def __init__(self, bot):
        self.bot = bot
        self.dbl_client = topgg.DBLClient(bot, TOPGG_API_TOKEN, autopost=True, session=bot.session)

    # async def post(self, count):
    #     endpoint = f'https://top.gg/api/bots/{self.bot.user.id}/stats'
    #     headers = {
    #         'Authorization': TOPGG_API_TOKEN
    #     }
    #     fields = {
    #         'server_count': count
    #     }

    #     resp = await self.bot.session.post(endpoint, data=fields, headers=headers)
    #     return resp

    # async def cog_load(self):
    #     self.post_guild_count.start()

    # @tasks.loop(hours=1)
    # async def post_guild_count(self):
    #     count = len(self.bot.guilds)
    #     resp = await self.post(count)

    #     if resp.status != 200:
    #         print(f'Posting stats failed with code {resp.status}')
    #         return 

    #     print(f'Posted guild count ({count}) to top.gg at {datetime.datetime.now().astimezone().strftime("%c")}')

    # @post_guild_count.before_loop
    # async def wait_until_hour(self):
    #     now = datetime.datetime.now().astimezone()
    #     next_run = now.replace(hour=0, minute=0, second=0)

    #     if next_run < now:
    #         next_run += datetime.timedelta(hours=1)

    #     await discord.utils.sleep_until(next_run)


async def setup(bot):
    await bot.add_cog(TopGG(bot))
