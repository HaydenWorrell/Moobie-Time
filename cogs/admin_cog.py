from logging import getLogger


from discord.ext import commands

from moobie_time.moobie_time import MoobieTime, permissions_check

log = getLogger(__name__)

class AdminCog(commands.Cog):
    def __init__(self, bot: MoobieTime):
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    def on_ready(self) -> None:
        log.info(f"Admin Cog ready")


    @commands.hybrid_command(name="removesuggestion")
    @commands.check(permissions_check)
    async def remove_suggestion(self, ctx: commands.Context, suggestion_id: str) -> None:
        pass
        #TODO: write function to remove suggestions from the list





