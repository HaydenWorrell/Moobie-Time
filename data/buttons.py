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
        self.interaction = ctx.interaction
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.ctx.bot.push_movie(self.ctx, self.movie)
        # await self.ctx.interaction.message.delete()


class ButtonView(discord.ui.View):
    def __init__(
        self, ctx: commands.Context, movie_list: list[Movie], database: Database, is_link: bool, message: Message | None
    ) -> None:
        super().__init__(timeout=300)
        self.movie_list = movie_list
        self.database = database
        self.message = message
        self.is_link = is_link
        if self.is_link:
            self.build_buttons_link(ctx)
        if not self.is_link:
            self.build_buttons_suggest(ctx)

    async def on_timeout(self):
        log.info("button timeout")
        try:
            await self.message.delete()
        except commands.errors.BadArgument:
            log.exception("no message present to delete")

    def build_buttons_suggest(self, ctx: commands.Context) -> None:
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

    def build_buttons_link(self, ctx: commands.Context) -> None:
        [
            self.add_item(
                SelectButton(
                    style=discord.ButtonStyle["primary"],
                    label='Send it!',
                    database=self.database,
                    movie=movie,
                    ctx=ctx,
                )
            )
            for movie in self.movie_list
        ]
