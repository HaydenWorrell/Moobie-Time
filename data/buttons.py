from logging import getLogger
from typing import Any

import discord
from discord import Message
from discord.ext import commands

from data.database import Database
from data.movie import Movie

log = getLogger(__name__)


class SelectButton(discord.ui.Button):
    def __init__(self, ctx: commands.Context, movie: Movie, database: Database, **kwargs: Any) -> None:
        self.database = database
        self.movie = movie
        self.ctx = ctx
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction) -> None:

        if existing_movie := self.database.from_movie_id(self.movie.id):
            existing_msg = await self.ctx.channel.fetch_message(existing_movie.message_id)
            await interaction.response.send_message(
                f"Could not add {self.movie.name} to the database, already exists here: "
                f"{existing_msg.jump_url}",
                ephemeral=True,
            )

        else:
            message = await interaction.channel.send(embed=self.movie.to_embed())
            await message.add_reaction('💖')
            movie_obj = self.movie.to_db(message_id=message.id)

            if self.database.add(movie_obj):
                await interaction.response.send_message(
                    f"Successfully added {self.movie.name} to the database",
                    ephemeral=True,
                )

            else:
                await interaction.response.send_message(
                    f"Could not add {self.movie.name} to the database",
                    ephemeral=True,
                )

        await interaction.message.delete()


class ButtonView(discord.ui.View):
    def __init__(self, ctx: commands.Context, movie_list: list[Movie], database: Database) -> None:
        super().__init__(timeout=300)
        self.movie_list = movie_list
        self.database = database
        self.message = None
        self.build_buttons(ctx)

    async def on_timeout(self):
        await self.message.delete()
        log.info("button timeout")

    def build_buttons(self, ctx: commands.Context) -> None:
        [
            self.add_item(
                SelectButton(
                    style=discord.ButtonStyle["primary"],
                    label=i + 1,
                    database=self.database,
                    movie=movie,
                    ctx=ctx,
                )
            )
            for i, movie in enumerate(self.movie_list)
        ]
