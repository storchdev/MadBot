from discord.ext import commands
import re
from datetime import datetime


splitter = re.compile('([.!?] *)')


class CannotEmbedLinks(commands.BotMissingPermissions):
    pass


class Blacklisted(commands.CheckFailure):
    pass


def is_blacklisted(ctx):
    if ctx.author.id in ctx.bot.blacklisted and ctx.author.id != 553058885418876928:
        raise Blacklisted()
    return True


def embed_links(ctx):
    if not ctx.channel.permissions_for(ctx.me).embed_links:
        raise CannotEmbedLinks(['embed_links'])
    return True


def readable(timestamp: int):
    dt = datetime.utcfromtimestamp(timestamp - 18000)
    return dt.strftime('%m/%d/%Y at %I:%M:%S %p EST')


def capitalize(text: str):
    split = splitter.split(text)
    final_story = []
    for sentence in split:
        if len(sentence) < 2:
            final_story.append(sentence)
        else:
            final_story.append(sentence[0].upper() + sentence[1:])
    return ''.join(final_story)
