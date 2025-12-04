from logging import getLogger
from pathlib import Path

import discord
from discord import Embed
from discord.ext import commands

from data.database import Database
from data.movie import Movie
from moobie_time import MoobieTime
from data.movie_entry import MovieBase
from searcher import SearchBoi
from config.config import Config
from moobie_time import MoobieTime

log = getLogger(__name__)


class UserCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("User Cog loaded")



    @commands.hybrid_command(name="suggest")
    async def suggest(self, ctx: commands.Context, movie_name: str) -> None:
        movie_search = SearchBoi()

        try:
            result: Movie = movie_search.search(movie_name=movie_name)
            db_movie: MovieBase = result.to_db(ctx.author.id, sum((react.count for react in ctx.message.reactions)), ctx.message.id)
            self.bot.database.add(db_movie)

            if not self.bot.database.add(db_movie):
                await ctx.send(f"Failed to add {movie_name}")


        except Exception:
            log.exception(f"Failed to add {movie_name}")
            return

        result_url: str = result.construct_url()

        embed: Embed = discord.Embed(title=movie_name, color=discord.Color.green(), url=result_url)

        await ctx.send(embed=embed)

async def setup(bot: MoobieTime):
    await bot.add_cog(UserCog(bot))