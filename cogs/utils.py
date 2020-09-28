from discord.ext import commands


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


intervals = {
    'weeks': 604800,
    'days': 86400,
    'hours': 3600,
    'minutes': 60,
    'seconds': 1
}


def humanize(seconds: float):
    seconds = int(seconds)
    result = []

    for name in intervals:
        amount = intervals[name]
        value = seconds // amount
        if value:
            seconds -= value * amount
            if value == 1:
                name = name.rstrip('s')
            result.append(f'{value} {name}')
    return ', '.join(result)
