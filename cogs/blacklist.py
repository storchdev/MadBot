from discord.ext import commands 
import discord 
import time


class Blacklisted(commands.CheckFailure):
    pass
    
    
def is_blacklisted(ctx):
    if ctx.author.id in ctx.bot.blacklisted and ctx.author.id != 553058885418876928:
        raise Blacklisted(f'{ctx.author} is blacklisted.')
    return True 


class Blacklist(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.bot.Blacklisted = Blacklisted
        self.bot.loop.create_task(self.get_blacklisted())
        
    async def get_blacklisted(self):
        query = 'SELECT user_id FROM blacklisted'
        user_ids = [row['user_id'] for row in await self.bot.db.fetch(query)]
        self.bot.blacklisted = user_ids
        self.bot.add_check(is_blacklisted)
    
    @commands.command(aliases=['bl'])
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.User, *, reason):
        self.bot.blacklisted.append(user.id)
        query = 'INSERT INTO blacklisted (user_id, timestamp, reason) VALUES ($1, $2, $3)'
        await self.bot.db.execute(query, user.id, int(time.time()), reason)
        await ctx.send(f':thumbsup: {user} was blacklisted.')

    @commands.command(aliases=['ubl'])
    @commands.is_owner()
    async def unblacklist(self, ctx, *, user: discord.User):
        self.bot.blacklisted.remove(user.id)
        query = 'DELETE FROM blacklisted WHERE user_id = $1'
        await self.bot.db.execute(query, user.id)
        await ctx.send(f':thumbsup: {user} was unblacklisted.')


def setup(bot):
    bot.add_cog(Blacklist(bot))
