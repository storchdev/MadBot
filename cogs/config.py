from discord.ext import commands


class Config(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='prefix')
    async def _prefix(self, ctx, new_prefix: str = ''):

        if not new_prefix:
            current = ctx.prefix 
            return await ctx.send(f'The current prefix is `{current}`.')

        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions(['manage_guild'])

        prefix = new_prefix.lstrip()
        if len(prefix) > 16:
            return await ctx.send(f'The prefix must be 16 characters or under.')

        if ctx.guild.id not in self.bot.prefixes:
            query = 'INSERT INTO prefixes (prefix, guild_id) VALUES ($1, $2)'
        else:
            query = 'UPDATE prefixes SET prefix = $1 WHERE guild_id = $2'

        self.bot.prefixes[ctx.guild.id] = prefix
        await self.bot.db.execute(query, prefix, ctx.guild.id)

        await ctx.send(f'Prefix changed to `{prefix}`. Do `{prefix}prefix` again to change it.')
        

def setup(bot):
    bot.add_cog(Config(bot))
