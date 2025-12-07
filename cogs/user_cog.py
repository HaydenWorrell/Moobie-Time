from logging import getLogger
from pathlib import Path

import discord
from discord import Embed, app_commands
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
            results: list[Movie] = movie_search.search(movie_name=movie_name)

            if not results:
                await ctx.send(f"Failed to find results for {movie_name}", ephemeral=True)
                return

            db_movie_list = []

            for result in results:
                db_movie_list.append(result.to_db(ctx.author.id, sum((react.count for react in ctx.message.reactions)), ctx.message.id))

        except Exception:
            log.exception(f"Failed to build db_movie_list")
            return



        embed: Embed = discord.Embed(title=f'Movie Results', description=self.build_embed_text(results), color=discord.Color.green())

        await ctx.send(embed=embed)

    @staticmethod
    def build_embed_text(movie_list: list[Movie]) -> str:
        return '\n'.join([f"[{movie.name}({movie.year})]({movie.construct_url()})" for movie in movie_list])

async def setup(bot: MoobieTime):
    await bot.add_cog(UserCog(bot))