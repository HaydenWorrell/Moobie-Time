from logging import getLogger

from discord.ext import commands

from moobie_time import MoobieTime
from data.movie_entry import MovieBase

log = getLogger(__name__)


class UserCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    def on_ready(self) -> None:
        log.info("User Cog loaded")

    @commands.hybrid_command(name="suggest")
    async def suggest(self, ctx: commands.Context, movie_name: str) -> None:
        pass
