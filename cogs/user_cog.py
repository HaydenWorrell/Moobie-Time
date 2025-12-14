from logging import getLogger

import discord
from discord import Embed
from discord.ext import commands

from data.buttons import ButtonView
from data.movie import Movie
from moobie_time import MoobieTime
from searcher import SearchBoi

log = getLogger(__name__)


async def channel_check(ctx: commands.Context) -> bool:
    if ctx.channel.id == int(ctx.bot.config.suggest_channel):
        return True

    channel = ctx.bot.get_channel(int(ctx.bot.config.suggest_channel))

    await ctx.send(f"Please use the {channel.mention} channel for suggestions.", ephemeral=True)
    return False


class UserCog(commands.Cog):
    def __init__(self, bot: MoobieTime) -> None:
        self.bot: MoobieTime = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("User Cog loaded")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent) -> None:
        if reaction.channel_id != int(self.bot.config.suggest_channel) or reaction.member.bot:
            log.info("incorrect channel")

            return
        channel = self.bot.get_channel(reaction.channel_id)
        msg = await channel.fetch_message(reaction.message_id)

        if str(reaction.emoji) != '💖':
            await msg.remove_reaction(reaction.emoji, reaction.member)
            log.info("incorrect reaction")
            return

        if not (movie := self.bot.database.from_message(reaction.message_id)):
            log.info("no movie found")
            return
        movie.reaction_count = msg.reactions[0].count if msg.reactions else 0


        self.bot.database.update_reactions(movie)
        log.info(f"Updated reactions for {movie.name} to {movie.reaction_count}")

    @commands.hybrid_command(name="suggest")
    @commands.check(channel_check)
    async def suggest(self, ctx: commands.Context, movie_name: str) -> None:
        movie_search = SearchBoi()

        try:
            results: list[Movie] = movie_search.search(movie_name=movie_name)

            if not results:
                await ctx.send(f"Failed to find results for {movie_name}", ephemeral=True)
                return

        except RuntimeError:
            log.exception("Failed to build db_movie_list")
            return

        embed: Embed = discord.Embed(
            title='Movie Results', description=self.build_embed_text(results), color=discord.Color.green()
        )

        await ctx.send(embed=embed, view=ButtonView(ctx, results, self.bot.database))

    @staticmethod
    def build_embed_text(movie_list: list[Movie]) -> str:
        return '\n'.join([
            f"{i + 1} [{movie.name} ({movie.year})]({movie.construct_url()})" for i, movie in enumerate(movie_list)
        ])


async def setup(bot: MoobieTime):
    await bot.add_cog(UserCog(bot))
