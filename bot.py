from database import db
from discord.ext import commands 
from config import TOKEN 

db, prefixes = db.db, db.prefixes
 

def get_prefix(client, message):
    prefix = prefixes.get(message.guild.id)
    return prefix if prefix else 'ml!'


bot = commands.Bot(command_prefix=get_prefix)
bot.db = db
bot.prefixes = prefixes

for cog in ['config', 'listeners', 'madlibs']:
    bot.load_extension('cogs.' + cog)

bot.load_extension('jishaku')   
bot.run(TOKEN)
