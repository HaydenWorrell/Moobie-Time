from logging import getLogger

import discord

log = getLogger(__name__)


class ButtonView(discord.ui.View):

    @discord.ui.button(label="Click me", style=discord.ButtonStyle["blurple"])
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(content="You did it!", ephemeral=False)
