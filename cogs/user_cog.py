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

        if str(reaction.emoji) != '💖' and str(reaction.emoji) != '✅':
            await msg.remove_reaction(reaction.emoji, reaction.member)
            log.info("incorrect reaction")
            return
        if str(reaction.emoji) == '✅' and not any(
            role for role in reaction.member.roles if role.id == self.bot.config.admin_role
        ):
            await msg.remove_reaction(reaction.emoji, reaction.member)
            log.info("non-admin tried to apply check mark")
            return
        if not (movie := self.bot.database.from_message(reaction.message_id)):
            log.info("no movie found")
            return
        if str(reaction.emoji) == '✅' and any(
            role for role in reaction.member.roles if role.id == self.bot.config.admin_role
        ):
            movie.watched = True
            log.info("movie marked as watched")
            return

        movie.reaction_count = msg.reactions[0].count if msg.reactions else 0
        self.bot.database.update_reactions(movie)

        log.info(f"Updated reactions for {movie.name} to {movie.reaction_count}")

    @commands.hybrid_command(name="suggest")
    @commands.check(channel_check)
    async def suggest(self, ctx: commands.Context, movie_name: str) -> None:
        if not (results := SearchBoi().search(movie_name=movie_name)):
            await ctx.send(f"Failed to find results for {movie_name}", ephemeral=True)
            return
        embed: Embed = discord.Embed(
            title='Movie Results',
            description=self.build_embed_text(results),
            color=discord.Color.green(),
        )
        msg_view = ButtonView(
            ctx,
            results,
            self.bot.database,
            is_link=False,
        )
        msg = await ctx.send(
            embed=embed,
            view=msg_view,
        )
        msg_view.message = msg

    @commands.hybrid_command(name="suggestlink")
    @commands.check(channel_check)
    async def suggestlink(self, ctx: commands.Context, movie_link: str) -> None:
        if not (movie_slug := movie_link.split("/")[-1] if len(movie_link.split("/")) > 1 else None):
            await ctx.send(f"Unable to find or extract movie slug in {movie_link}", ephemeral=True)
            return
        if not (result := SearchBoi().db.get_movie_by_slug(movie_slug)):
            await ctx.send(f"No movie found with slug {movie_slug}", ephemeral=True)
            return
        correct_movie_as_lst = [
            Movie(
                id=str(result["id"]),
                name=result["name"],
                image=result["image"],
                year=result["year"],
                slug=result["slug"],
            )
        ]
        embed: Embed = correct_movie_as_lst[0].to_embed()
        msg_view: ButtonView = ButtonView(
            ctx,
            correct_movie_as_lst,
            self.bot.database,
            is_link=True,
        )
        msg = await ctx.send(
            embed=embed,
            view=msg_view,
        )
        msg_view.message = msg

    @staticmethod
    def build_embed_text(movie_list: list[Movie]) -> str:
        return '\n'.join([
            f"{i + 1}. [{movie.name} ({movie.year})]({movie.construct_url()})" for i, movie in enumerate(movie_list)
        ])


async def setup(bot: MoobieTime):
    await bot.add_cog(UserCog(bot))
