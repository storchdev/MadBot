import dbl
from discord.ext import commands
from config import TOPGG_API_TOKEN


class TopGG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.DBLClient(self.bot, TOPGG_API_TOKEN, autopost=True)

    @commands.command()
    async def vote(self, ctx):
        await ctx.send('https://top.gg/bot/742921922370600991/vote\n\n**Thanks for your support!**')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        await self.bot.get_user(553058885418876928).send(data)


def setup(bot):
    bot.add_cog(TopGG(bot))
