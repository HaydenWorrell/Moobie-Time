import time
from logging import getLogger

from discord.ext import commands

from csvreader import build_movie_list
from data.movie import Movie
from moobie_time import MoobieTime, permissions_check

log = getLogger(__name__)
movie_list = build_movie_list()
watched_movies = [movie for movie in movie_list if movie.watched]
unwatched_movies = [mov for mov in movie_list if not mov.watched]


class AdminCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("Admin Cog loaded")

    @commands.hybrid_command(name="importwatched")
    @commands.check(permissions_check)
    async def csv_import_watched(self, ctx: commands.Context) -> None:
        channel = await ctx.bot.fetch_channel(int(ctx.bot.config.target_channel))
        for movie in watched_movies:
            embed = movie.to_embed()
            msg = await channel.send(embed=embed)
            ctx.bot.database.add(movie.to_db(message_id=msg.id))
            await msg.add_reaction('💖')
            await msg.add_reaction('✅')

            time.sleep(1)
        log.info("watched_movies imported successfully")

    @commands.hybrid_command(name="import")
    @commands.check(permissions_check)
    async def csv_import_unwatched(self, ctx: commands.Context) -> None:
        channel = await ctx.bot.fetch_channel(int(ctx.bot.config.target_channel))
        for movie in unwatched_movies:
            embed = movie.to_embed()
            msg = await channel.send(embed=embed)
            ctx.bot.database.add(movie.to_db(message_id=msg.id))
            await msg.add_reaction('💖')

            time.sleep(1)

    @commands.hybrid_command(name="addmovie")
    @commands.check(permissions_check)
    async def add_movie(
        self,
        ctx: commands.Context,
        movie_title: str,
        link: str,
        tvdb_id: str | None = None,
        year: str = 'unknown',
        slug: str = '',
        watched: bool = False,
    ) -> None:
        movie: Movie = Movie(
            tvdb_id=tvdb_id or movie_title,
            name=movie_title,
            year=year,
            slug=slug,
            watched=watched,
        )
        await ctx.bot.push_movie(
            ctx=ctx,
            movie=movie,
            link=link,
        )

    @commands.hybrid_command(name="removemovie")
    @commands.check(permissions_check)
    async def remove(self, ctx: commands.Context, movie_name: str) -> None:
        if self.bot.database.remove(movie_name):
            await ctx.reply(f"Successfully removed {movie_name} from database", ephemeral=True)
        else:
            await ctx.reply(f"Failed to remove {movie_name} from database", ephemeral=True)


async def setup(bot: MoobieTime):
    await bot.add_cog(AdminCog(bot))
