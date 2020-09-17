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

        query = 'INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ' \
                'ON CONFLICT (guild_id) DO UPDATE SET prefix = $2'
        self.bot.prefixes[ctx.guild.id] = prefix
        await self.bot.db.execute(query, ctx.guild.id, prefix)

        await ctx.send(f'Prefix changed to `{prefix}`. Do `{prefix}{ctx.command.name}` again to change it.')
        

def setup(bot):
    bot.add_cog(Config(bot))
