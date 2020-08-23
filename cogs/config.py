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
        
        if ctx.guild.id not in list(self.bot.prefixes.keys()):
            query = 'INSERT INTO prefixes (prefix, guild_id) VALUES (?, ?)'
        else:
            query = 'UPDATE prefixes SET prefix = ? WHERE guild_id = ?'
            
        self.bot.prefixes[ctx.guild.id] = prefix
        async with self.bot.db.cursor() as cur:
            await cur.execute(query, (prefix, ctx.guild.id))
            await self.bot.db.commit()

        await ctx.send(f'Prefix changed to `{prefix}`. Do `{prefix}prefix` again to change it.')
        

def setup(bot):
    bot.add_cog(Config(bot))
