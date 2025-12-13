from logging import getLogger

from discord.ext import commands

from moobie_time import MoobieTime, permissions_check

log = getLogger(__name__)


class AdminCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info(f"Admin Cog loaded")

    @commands.hybrid_command(name="watched")
    @commands.check(permissions_check)
    async def watched(self, ctx: commands.Context, movie_name: str) -> None:
        pass

    @commands.hybrid_command(name="removemovie")
    @commands.check(permissions_check)
    async def remove(self, ctx: commands.Context, movie_name: str) -> None:
        if self.bot.database.remove(movie_name):
            await ctx.reply(f"Successfully removed {movie_name} from database", ephemeral=True)
        else:
            await ctx.reply(f"Failed to remove {movie_name} from database", ephemeral=True)


async def setup(bot: MoobieTime):
    await bot.add_cog(AdminCog(bot))
