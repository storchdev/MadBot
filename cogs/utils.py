from discord.ext import commands
import re
from humanize import precisedelta


splitter = re.compile('([.!?] *)')
placeholder = re.compile('{(.+?)}')
vowel = re.compile('^([aeiou])')


class CannotEmbedLinks(commands.BotMissingPermissions):
    pass


def embed_links(ctx):
    if not ctx.channel.permissions_for(ctx.me).embed_links:
        raise CannotEmbedLinks(['embed_links'])
    return True


def capitalize(text: str):
    split = splitter.split(text)
    final_story = []
    for sentence in split:
        if len(sentence) < 2:
            final_story.append(sentence)
        else:
            final_story.append(sentence[0].upper() + sentence[1:])
    return ''.join(final_story)


async def handle_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.NotOwner):
        await ctx.send(f':no_entry: This command is restricted for the owner.')
    elif isinstance(error, ctx.bot.CannotEmbedLinks):
        await ctx.send(f':no_entry: I need the `Embed Links` permission to be able to talk freely!')
    elif isinstance(error, commands.CommandOnCooldown):
        rate, per = error.cooldown.rate, error.cooldown.per
        s = '' if rate == 1 else 's'
        await ctx.send(f':no_entry: You can only use this command {rate} time{s} every {precisedelta(per)}. '
                        f'Please wait another `{error.retry_after:.2f}` seconds.')