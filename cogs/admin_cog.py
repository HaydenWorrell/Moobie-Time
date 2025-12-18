from logging import getLogger

from discord.ext import commands

from data.movie import Movie
from moobie_time import MoobieTime, permissions_check

log = getLogger(__name__)
# movie_list = build_movie_list()


class AdminCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("Admin Cog loaded")

    # @commands.hybrid_command(name="watched")
    # @commands.check(permissions_check)
    # async def watched(self, ctx: commands.Context, movie_name: str) -> None:
    #     pass

    # @commands.hybrid_command(name="import")
    # @commands.check(permissions_check)
    # async def csv_import(self, ctx: commands.Context) -> None:
    #
    #     for movie in movie_list:
    #         embed = movie.to_embed()
    #         msg = await ctx.send(embed=embed)
    #         ctx.bot.database.add(movie.to_db(message_id=msg.id))
    #         await msg.add_reaction('💖')
    #         if movie.watched:
    #             await msg.add_reaction('✅')
    #
    #         time.sleep(1)

    @commands.hybrid_command(name="addmovie")
    @commands.check(permissions_check)
    async def add_movie(
        self,
        ctx: commands.Context,
        movie_title: str,
        link: str,
        year: str = 'unknown',
        slug: str = '',
        watched: bool = False,
    ) -> None:
        movie: Movie = Movie(
            tvdb_id=movie_title,
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
