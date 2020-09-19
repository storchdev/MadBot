import discord
from discord.ext import commands
import asyncio
from concurrent.futures import TimeoutError


EMOJIS = (
    '\U0001f500',
    '\U000023ee',
    '\U000025c0',
    '\U000025b6',
    '\U000023ed'
)


async def create_embed(ctx, pagination):
    page = pagination['page']
    is_custom = pagination['on_custom']
    paginator = commands.Paginator(max_size=500, prefix='', suffix='')
    i = 1

    embed = discord.Embed(color=discord.Colour.blue())
    embed.add_field(
        name='THE HOST: TYPE OUT THE NUMBER OF THE TEMPLATE TO CHOOSE IT',
        value=f'Press {EMOJIS[0]} to switch between custom and default templates.'
    )

    if not is_custom:

        for template in ctx.bot.defaults:
            line = f'`{i}.` **{template}** ({ctx.bot.lengths[template]} blanks)'
            paginator.add_line(line)
            i += 1

        pages = paginator.pages
        embed.set_author(name=f'Page {page}/{len(pages)}')
        embed.title = f'{len(ctx.bot.defaults)} Default Templates'
        embed.description = pages[page - 1]

    else:
        rows = await ctx.bot.db.fetch(
            'SELECT name, template FROM madlibs WHERE guild_id = $1', ctx.guild.id
        )
        i = len(ctx.bot.defaults) + 1
        embed.title = f'{len(rows)} Custom Templates'

        if rows:
            for row in rows:
                blanks = len(ctx.bot.finder.findall(row['template']))
                line = f'`{i}.` **{row[0]}** ({blanks} blanks)'
                paginator.add_line(line)
                i += 1

            pages = paginator.pages
            embed.description = pages[page - 1]
            embed.set_author(name=f'Page {page}/{len(pages)}')
        else:
            embed.description = 'No custom templates found.'
            return embed, 0

    return embed, len(pages)


async def menu(ctx, message, pagination):
    embed, max_length = await create_embed(ctx, pagination)
    [await message.add_reaction(emoji) for emoji in EMOJIS]

    def check(r, u):
        return u.id == ctx.author.id and str(r) in EMOJIS

    while True:
        try:
            done, pending = await asyncio.wait([
                ctx.bot.wait_for('reaction_add', timeout=30, check=check),
                ctx.bot.wait_for('reaction_remove', timeout=30, check=check)
            ], return_when=asyncio.FIRST_COMPLETED)

            emoji = done.pop().result()[0].emoji
            for future in done:
                future.exception()
            for future in pending:
                future.cancel()
        except TimeoutError:
            await message.delete()
            return

        if emoji == EMOJIS[0]:
            if pagination['on_custom']:
                pagination['on_custom'] = False
            else:
                pagination['on_custom'] = True
            embed = (await create_embed(ctx, pagination))[0]
            pagination['page'] = 1
            await message.edit(embed=embed)
        elif emoji == EMOJIS[1]:
            pagination['page'] = 1
            embed = (await create_embed(ctx, pagination))[0]
            await message.edit(embed=embed)
        elif emoji == EMOJIS[2]:
            if pagination['page'] > 1:
                pagination['page'] -= 1
                embed = (await create_embed(ctx, pagination))[0]
                await message.edit(embed=embed)
        elif emoji == EMOJIS[3]:
            if pagination['page'] < max_length:
                pagination['page'] += 1
                embed = (await create_embed(ctx, pagination))[0]
                await message.edit(embed=embed)
        elif emoji == EMOJIS[4]:
            if pagination['page'] != max_length:
                pagination['page'] = max_length
                embed = (await create_embed(ctx, pagination))[0]
                await message.edit(embed=embed)
