from logging import getLogger

from discord.ext import commands

from moobie_time import MoobieTime, permissions_check

log = getLogger(__name__)


class AdminCog(commands.Cog):
    def __init__(self, bot: MoobieTime):
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    def on_ready(self) -> None:
        log.info(f"Admin Cog loaded")

    @commands.hybrid_command(name="suggest")
    @commands.check(permissions_check)
    async def suggest(self, ctx: commands.Context) -> None:
        pass
