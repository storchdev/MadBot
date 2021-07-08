import discord


class ViewMenu(discord.ui.View):

    def __init__(self, ctx, embeds, *, timeout=180):
        super().__init__(timeout=timeout)
        self.page = 0
        self.embeds = embeds
        self.ctx = ctx

    async def interaction_check(self, interaction):
        return self.ctx.author == interaction.user

    async def update_view(self, interaction):
        embed = self.embeds[self.page]
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u23ee')
    async def beginning(self, button, interaction):
        if len(self.embeds) == 0:
            return
        if self.page == 0:
            return
        self.page = 0
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u25c0')
    async def previous(self, button, interaction):
        if len(self.embeds) == 0:
            return
        if self.page == 0:
            return
        self.page -= 1
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u25b6')
    async def next(self, button, interaction):
        if len(self.embeds) == 0:
            return
        if self.page == len(self.embeds) - 1:
            return
        self.page += 1
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u23ed')
    async def end(self, button, interaction):
        if len(self.embeds) == 0:
            return
        if self.page == len(self.embeds) - 1:
            return
        self.page = len(self.embeds) - 1
        await self.update_view(interaction)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button, interaction):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()


class TemplatesMenu(ViewMenu):

    def __init__(self, ctx, default, custom, default_options, custom_options):
        super().__init__(ctx, default, timeout=None)
        self.embeds = default
        self.default = default
        self.custom = custom
        self.default_options = default_options
        self.custom_options = custom_options
        self.add_item(self.get_select())
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label == 'Cancel':
                    self.remove_item(item)
                    break

    def get_select(self):
        if self.embeds == self.default:
            options = self.default_options[self.page]
        else:
            try:
                options = self.custom_options[self.page]
            except KeyError:
                return

        selectoptions = []
        for n, info in options.items():
            selectoptions.append(discord.SelectOption(label=n, description=info[0]))
        select = discord.ui.Select(placeholder='Choose a template', options=selectoptions)

        async def callback(interaction):
            n2 = interaction.data['values'][0]
            info2 = options[int(n2)]
            name = info2[0]
            template = info2[1]

            self.ctx.bot.dispatch('select', interaction.user, name, template)
            self.clear_items()
            await interaction.response.edit_message(
                content=f'Selected: **{n2}. {name}**',
                view=self, embed=None
            )

        select.callback = callback
        return select

    async def update_view(self, i):
        if len(self.embeds) == 0:
            embed = discord.Embed(
                title='No Custom Templates',
                color=self.ctx.author.color
            )
        else:
            embed = self.embeds[self.page]
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
                break
        select = self.get_select()
        if select is not None:
            self.add_item(select)
        await i.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Default Templates', style=discord.ButtonStyle.blurple, row=2)
    async def default(self, button, interaction):
        if self.embeds == self.default:
            return
        self.embeds = self.default
        self.page = 0
        await self.update_view(interaction)

    @discord.ui.button(label='Custom Templates', style=discord.ButtonStyle.blurple, row=2)
    async def custom(self, button, interaction):
        if self.embeds == self.custom:
            return
        self.embeds = self.custom
        self.page = 0
        await self.update_view(interaction)


class YesNo(discord.ui.View):

    def __init__(self, ctx, name, story, participants):
        self.ctx = ctx
        self.bot = ctx.bot
        self.story = story
        self.name = name
        self.participants = participants
        super().__init__(timeout=15)

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @discord.ui.button(label='Send!', style=discord.ButtonStyle.green)
    async def yes(self, button, interaction):
        ch = self.bot.get_channel(765759340405063680)
        if len(self.story) > 2042:
            self.story = self.story[:2041]
        embed = discord.Embed(
            title=self.name,
            description=f'```{self.story}```',
            color=discord.Colour.orange()
        )
        embed.add_field(name='Participants', value=', '.join(u.name for u in self.participants))
        await ch.send(embed=embed)

        button.disabled = True
        button.label = 'Sent!'
        await self.message.edit(view=self)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.gray)
    async def no(self, button, interaction):
        await self.message.delete()
        self.stop()
