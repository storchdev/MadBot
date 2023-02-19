from discord.ext import commands 
from discord import app_commands
from humanize import precisedelta 
import discord 
from typing import Optional 

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot 
        
    async def upsert(self, guild, column, value):
        query = f"""INSERT INTO settings (guild_id, {column})
                    VALUES ($1, $2)
                    ON CONFLICT (guild_id) DO UPDATE 
                    SET {column} = $2
                """
        await self.bot.db.execute(query, guild.id, value)

    @app_commands.default_permissions()
    @app_commands.describe(timeout='seconds')
    @app_commands.command(name='time-limit')
    async def time_limit(self, interaction, timeout: Optional[app_commands.Range[int, 5]]):
        """Sets the amount of time players have to enter their word before being removed from the game. Default is 45."""
        if timeout is None:
            timeout = 0
            timeoutstr = 'Infinite'
        else:
            timeoutstr = precisedelta(timeout)

        await self.upsert(interaction.guild, 'time_limit', timeout)
        await interaction.response.send_message(
            f'**SETTINGS:** Time for players to submit their word set to `{timeoutstr}`.'
        )

    @app_commands.default_permissions()
    @app_commands.describe(players='number of players')
    @app_commands.command(name='max-players')
    async def max_players(self, interaction, players: app_commands.Range[int, 1, 50]):
        """Sets the maximum amount of players who can join one game. Default is 10."""
        await self.upsert(interaction.guild, 'max_players', players)
        await interaction.response.send_message(
            f'**SETTINGS:** Maximum players per game set to `{players}`.'
        )

    @app_commands.default_permissions()
    @app_commands.describe(games='number of games')
    @app_commands.command(name='max-games')
    async def max_games(self, interaction, games: app_commands.Range[int, 1, 10]):
        """Sets the maximum games that can take place at any one time in a channel. Default is 1."""
        await self.upsert(interaction.guild, 'max_games', games)
        await interaction.response.send_message(
            f'**SETTINGS:** Maximum games per channel set to `{games}`.'
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
