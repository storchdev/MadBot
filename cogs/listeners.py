from discord.ext import commands
from discord import app_commands
from humanize import precisedelta
import traceback
import discord


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.tree_error

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.owner.send(f'I HAVE JOINED **{guild.name}**')

    async def tree_error(self, interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            rate = error.cooldown.rate
            per = precisedelta(int(error.cooldown.per))
            wait = precisedelta(error.retry_after)

            s = '' if error.cooldown.per == 1 else 's'

            await interaction.response.send_message(
                f':no_entry: You can only use this command {rate} time{s} every `{per}`.\n'
                f'Please try again in **{wait}**.',
                ephemeral=True
            )
        elif isinstance(error, app_commands.CheckFailure):
            pass
        else:
            etype = type(error)
            trace = error.__traceback__
            lines = traceback.format_exception(etype, error, trace)

            pag = commands.Paginator(prefix='```py\n', max_size=2048)
            for line in lines:
                pag.add_line(line)

            embed = discord.Embed(
                title=f'Error in {interaction.command.name}',
                color=discord.Colour.red(),
                description=pag.pages[0]
            ).add_field(
                name='Author', value=f'{interaction.user}\n{interaction.user.mention}'
            ).add_field(
                name='Channel', value=f'#{interaction.channel}\n{interaction.channel.mention}'
            ).add_field(
                name='Guild', value=interaction.guild.name
            )
            await self.bot.owner.send(embed=embed)

            for page in pag.pages[1:]:
                embed = discord.Embed(
                    description=page,
                    color=discord.Colour.red()
                )
                await self.bot.owner.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Listeners(bot))
