from discord.ext import commands
from discord import app_commands as slash
from humanize import precisedelta


class Listeners(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.tree_error
        self.owner = None

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.owner.send(f'I HAVE JOINED **{guild.name}**')

    async def tree_error(self, interaction, error):
        if isinstance(error, slash.CommandOnCooldown):
            rate = error.cooldown.rate
            per = precisedelta(int(error.cooldown.per))
            wait = precisedelta(error.retry_after)

            s = '' if error.cooldown.per == 1 else 's'

            await interaction.response.send_message(
                f':no_entry: You can only use this command {rate} time{s} every `{per}`.\n'
                f'Please try again in **{wait}**.',
                ephemeral=True
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Listeners(bot))
