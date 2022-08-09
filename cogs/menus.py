import discord


class ViewMenu(discord.ui.View):

    def __init__(self, interaction, embeds, *, timeout=180):
        super().__init__(timeout=timeout)
        self.page = 0
        self.embeds = embeds
        self.interaction = interaction 

    async def interaction_check(self, interaction):
        return self.interaction.user == interaction.user

    async def update_view(self, interaction):
        embed = self.embeds[self.page]
        await interaction.response.edit_message(embed=embed)

    async def update_from_modal(self, interaction):
        embed = self.embeds[self.page]
        await self.message.edit(embed=embed)
        await interaction.response.send_message(f'Jumped to page {self.page + 1}.', ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u23ee')
    async def beginning(self, interaction, button):
        if len(self.embeds) == 0:
            return
        if self.page == 0:
            return
        self.page = 0
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u25c0')
    async def previous(self, interaction, button):
        if len(self.embeds) == 0:
            return
        if self.page == 0:
            return
        self.page -= 1
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u25b6')
    async def _next(self, interaction, button):
        if len(self.embeds) == 0:
            return
        if self.page == len(self.embeds) - 1:
            return
        self.page += 1
        await self.update_view(interaction)

    @discord.ui.button(style=discord.ButtonStyle.blurple, label='\u23ed')
    async def end(self, interaction, button):
        if len(self.embeds) == 0:
            return
        if self.page == len(self.embeds) - 1:
            return
        self.page = len(self.embeds) - 1
        await self.update_view(interaction)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, row=1)
    async def cancel(self, interaction, button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label='Jump', style=discord.ButtonStyle.gray)
    async def jump(self, interaction, button):

        class Modal(discord.ui.Modal, title='Enter a page to jump to.'):
            page = discord.ui.TextInput(label=f'1-{len(self.embeds)}', style=discord.TextStyle.short)

        async def on_submit(modal_i):
            try:
                page = int(self.page)
            except ValueError:
                await modal_i.response.send_message('You did not enter a number for the page.', ephemeral=True)
                return
            if page < 1:
                page = 1
            if page > len(self.embeds):
                page = len(self.embeds)

            self.page = page - 1
            await self.update_from_modal(modal_i)

        modal = Modal()
        modal.on_submit = on_submit

        await interaction.response.send_modal(modal)


class TemplatesMenu(ViewMenu):

    def __init__(self, interaction, default, custom, default_options, custom_options):
        super().__init__(interaction, default, timeout=180)
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
        self.name = None
        self.template = None

    def get_select(self):
        if self.embeds == self.default:
            options = self.default_options[self.page]
        else:
            try:
                options = self.custom_options[self.page]
            except KeyError:
                return

        if not options:
            return None 

        selectoptions = []
        for n, info in options.items():
            selectoptions.append(discord.SelectOption(label=n, description=info[0]))
        select = discord.ui.Select(placeholder='Choose a template', options=selectoptions)

        async def callback(interaction):
            n2 = interaction.data['values'][0]
            info2 = options[int(n2)]
            name = info2[0]
            template = info2[1]

            self.name = name
            self.template = template

            self.clear_items()
            await interaction.response.edit_message(
                content=f'Selected: **{n2}. {name}**',
                view=self, 
                embed=None
            )
            self.stop()

        select.callback = callback
        return select

    async def update_view(self, interaction):
        if len(self.embeds) == 0:
            embed = discord.Embed(
                title='No Custom Templates',
                color=self.interaction.user.color
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
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='Default Templates', style=discord.ButtonStyle.blurple, row=2)
    async def default(self, interaction, button):
        if self.embeds == self.default:
            return
        self.embeds = self.default
        self.page = 0
        await self.update_view(interaction)

    @discord.ui.button(label='Custom Templates', style=discord.ButtonStyle.blurple, row=2)
    async def custom(self, interaction, button):
        if self.embeds == self.custom:
            return
        self.embeds = self.custom
        self.page = 0
        await self.update_view(interaction)


class YesNo(discord.ui.View):

    def __init__(self, interaction, name, story, participants):
        self.interaction = interaction
        self.bot = interaction.client
        self.story = story
        self.name = name
        self.participants = participants
        self.message = None
        super().__init__(timeout=15)

    async def interaction_check(self, interaction):
        return interaction.user == self.interaction.user

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)
        self.stop()

    @discord.ui.button(label='Send!', style=discord.ButtonStyle.green)
    async def yes(self, interaction, button):
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
    async def no(self, interaction, button):
        await self.message.delete()
        self.stop()
