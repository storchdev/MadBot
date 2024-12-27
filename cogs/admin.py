from discord.ext import commands 
from discord import app_commands
from humanize import precisedelta 
import discord 
from typing import Optional, Literal
from cogs.menus import ClearHistoryYesNo


class Admin(commands.Cog):

    settings_cmd = app_commands.Group(name='settings', description='Change the settings for this server.')

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
    @settings_cmd.command(name='reset')
    async def reset_settings(self, interaction):
        """Resets all server settings to their default values."""
        query = 'DELETE FROM settings WHERE guild_id = $1'
        await self.bot.db.execute(query, interaction.guild.id)
        await interaction.response.send_message(
            ':thumbsup: **SETTINGS:** Time-limit, max-players, and max-games have been reverted to their default values.'
        )

    @app_commands.default_permissions()
    @app_commands.describe(timeout='seconds')
    @settings_cmd.command(name='time-limit')
    async def time_limit(self, interaction, timeout: Optional[app_commands.Range[int, 5]]):
        """Sets the amount of time players have to enter their word before being removed from the game. Default is 45."""
        if timeout is None:
            timeout = 0
            timeoutstr = 'Infinite'
        else:
            timeoutstr = precisedelta(timeout)

        await self.upsert(interaction.guild, 'time_limit', timeout)
        await interaction.response.send_message(
            f':thumbsup: **SETTINGS:** Time for players to submit their word set to `{timeoutstr}`.'
        )

    @app_commands.default_permissions()
    @app_commands.describe(players='number of players')
    @settings_cmd.command(name='max-players')
    async def max_players(self, interaction, players: app_commands.Range[int, 1, 50]):
        """Sets the maximum amount of players who can join one game. Default is 10."""
        await self.upsert(interaction.guild, 'max_players', players)
        await interaction.response.send_message(
            f':thumbsup: **SETTINGS:** Maximum players per game set to `{players}`.'
        )

    @app_commands.default_permissions()
    @app_commands.describe(games='number of games')
    @settings_cmd.command(name='max-games')
    async def max_games(self, interaction, games: app_commands.Range[int, 1, 10]):
        """Sets the maximum games that can take place at any one time in a channel. Default is 1."""
        await self.upsert(interaction.guild, 'max_games', games)
        await interaction.response.send_message(
            f':thumbsup: **SETTINGS:** Maximum games per channel set to `{games}`.'
        )

    @app_commands.default_permissions()
    @app_commands.command(name='clear-history')
    async def clear_history(self, interaction):
        """Clears all the past games in this server so that they won't appear in /history."""
        view = ClearHistoryYesNo(interaction)
        view.message = await interaction.response.send_message(
            ':warning: **Are you sure** about this action? It cannot be undone.',
            view=view
        )
    
    @app_commands.default_permissions()
    @app_commands.describe(mode='on or off')
    @settings_cmd.command(name='show-entered')
    async def show_entered(self, interaction, mode: Literal['on', 'off']):
        """Toggles whether or not to show what players entered after each turn."""

        if mode == 'on':
            mode = True 
        else:
            mode = False

        await self.upsert(interaction.guild, 'show_entered', mode)
        await interaction.response.send_message(
            f':thumbsup: **SETTINGS:** Show entered words set to `{mode}`.'
        )


        
async def setup(bot):
    await bot.add_cog(Admin(bot))
