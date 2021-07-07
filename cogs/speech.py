from discord.ext import commands
import json


class PartsOfSpeech(commands.Cog, name='Parts of Speech',
                    description='In case you forgot to pay attention in English class.'):

    def __init__(self, bot):
        self.bot = bot

        with open('./cogs/json/speech.json') as f:
            self.speech = json.load(f)

    @commands.group(invoke_without_command=True, aliases=['partsofspeech', 'speech'])
    async def pos(self, ctx):
        """Gives information on the main parts of speech, i.e. noun, adjective, verb, adverb."""
        text = f'''**There are 4 main parts of speech in MadLibs:**  `noun`, `adjective`, `verb`, `adverb`.
To get more info, you can use `{ctx.prefix.lower()}{ctx.invoked_with} <part of speech>`.'''
        await ctx.send(text)

    @pos.command()
    async def noun(self, ctx):
        """Gives information on what a noun is."""
        await ctx.send(self.speech['noun'])

    @pos.command()
    async def adverb(self, ctx):
        """Gives information on what an adverb is."""
        await ctx.send(self.speech['adverb'])

    @pos.command()
    async def verb(self, ctx):
        """Gives information on what a verb is."""
        await ctx.send(self.speech['verb'])

    @pos.command()
    async def adjective(self, ctx):
        """Gives information on what an adjective is."""
        await ctx.send(self.speech['adjective'])


def setup(bot):
    bot.add_cog(PartsOfSpeech(bot))

