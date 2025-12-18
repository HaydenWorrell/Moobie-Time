from logging import getLogger

import discord
from discord import Colour, Embed
from discord.ext import commands

from data.buttons import ButtonView
from data.movie import Movie
from moobie_time import MoobieTime
from searcher import SearchBoi

log = getLogger(__name__)


async def channel_check(ctx: commands.Context) -> bool:
    if ctx.channel.id == int(ctx.bot.config.suggest_channel) or ctx.channel.id == int(ctx.bot.config.target_channel):
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
        if reaction.channel_id != int(self.bot.config.target_channel) or reaction.member.bot:
            log.info("incorrect channel")
            return
        channel = self.bot.get_channel(reaction.channel_id)
        msg = await channel.fetch_message(reaction.message_id)

        if str(reaction.emoji) != '💖' and str(reaction.emoji) != '✅' and not reaction.member.bot:
            await msg.remove_reaction(reaction.emoji, reaction.member)
            log.info("incorrect reaction")
            return
        if str(reaction.emoji) == '✅' and reaction.member.bot:
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
            self.bot.database.mark_watched(movie)
            log.info("movie marked as watched")
            return
        if str(reaction.emoji) == '💖':
            movie.reaction_count = msg.reactions[0].count if msg.reactions else 0
            self.bot.database.update_reactions(movie)
            log.info(f"Updated reactions for {movie.name} to {movie.reaction_count}")
            return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent) -> None:
        if reaction.channel_id != int(self.bot.config.target_channel):
            log.info("incorrect channel")
            return
        # channel = self.bot.get_channel(reaction.channel_id)
        # msg = await channel.fetch_message(reaction.message_id)

        if not (movie := self.bot.database.from_message(reaction.message_id)):
            log.info("no movie found")
            return
        if str(reaction.emoji) == '💖':
            movie.reaction_count -= 1
            self.bot.database.update_reactions(movie)
            log.info(f"Updated reactions for {movie.name} to {movie.reaction_count}")
            return
        if str(reaction.emoji) == '✅':
            if self.bot.database.mark_unwatched(movie):
                log.info(f"Updated watched status for {movie.name} to {movie.watched}")
            return

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
            message=None,
        )
        msg = await ctx.send(embed=embed, view=msg_view, ephemeral=True)
        #     embed=embed,
        #     view=msg_view,
        # )
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
        correct_movie_as_lst = [Movie(**result, tvdb_id=str(result.get('id')))]
        embed: Embed = correct_movie_as_lst[0].to_embed()
        msg_view: ButtonView = ButtonView(
            ctx,
            correct_movie_as_lst,
            self.bot.database,
            is_link=True,
            message=None,
        )
        msg = await ctx.send(
            embed=embed,
            view=msg_view,
        )
        msg_view.message = msg

    @commands.hybrid_command(name="moviehelp")
    async def movie_help(self, ctx: commands.Context, command: str | None) -> None:
        if command is None or command == '':
            await ctx.send(
                "MoobieTime is a bot to manage suggestions for weekly movie nights! Suggesting a movie successfully will add it to our database, "
                "suggesting a movie that is already on our list will redirect you to the message containing a link with the tvdb.com page for the movie in question, "
                "the message will have a green check mark react (:white_check_mark:) if we have already watched it. "
                "Scroll through this channel to upvote (heart react) your favorite suggestions, "
                "as the reaction counts will be closely associated with which movies are chosen for the polls each week.\n\n"
                "**List of available commands:**\n\n"
                "**/suggest**\n"
                "**/suggestlink**\n"
                "**/topmovies**\n\n"
                "**/removemovie (MC Officer only)**\n\n"
                "**All commands will only work in the movie-suggestions channel**\n"
                "For help with a specific command, type '**/moviehelp <command>**', for example:\n"
                "'**/moviehelp suggest**'",
                ephemeral=True,
            )
            return
        if command.lower() == '/suggest' or command.lower() == 'suggest':
            await ctx.send(
                "Enter /suggest <movie name> and this will present a list of search results "
                "for you to choose from using the corresponding 1-5 buttons at the bottom of the message",
                ephemeral=True,
            )
            return
        if command.lower() == '/suggestlink' or command.lower() == 'suggestlink':
            await ctx.send(
                "Enter /suggest <tvdb link> and this will present a movie with a matching link, "
                "click the 'Send it!' button to confirm your choice and add the suggestion",
                ephemeral=True,
            )
            return
        if command.lower() == '/topmovies' or command.lower() == 'topmovies':
            await ctx.send(
                "Enter /topmovies to display an ordered list of the top 15 movies from the database, "
                "sorted by reaction count. Displayed as "
                "'1. <Movie name and hyperlink> (<Movie year>) - <Reaction count>'",
                ephemeral=True,
            )
            return
        if command.lower() == '/removemovie' or command.lower() == 'removemovie':
            await ctx.send(
                "Enter /removemovie <movie name> to remove a movie from the database. "
                "Make sure to delete the message it was attached to, functionality for that coming soon",
                ephemeral=True,
            )
            return
        await ctx.send(
            "Please enter a valid command, for example:\n'/moviehelp suggest'",
            ephemeral=True,
        )
        return

    @commands.hybrid_command(name="topmovies")
    @commands.check(channel_check)
    async def topmovies(self, ctx: commands.Context, count: int = 15) -> None:
        embed: Embed = Embed(
            title="Top Movies",
            description=self.build_top_movie_embed([
                Movie.from_db(moviebase) for moviebase in self.bot.database.get_top_movies(count)
            ]),
            colour=Colour.blue(),
        )
        await ctx.send(embed=embed, ephemeral=True)

    @staticmethod
    def build_embed_text(movie_list: list[Movie]) -> str:
        return '\n'.join([
            f"{i + 1}. [{movie.name} ({movie.year})]({movie.construct_url()})" for i, movie in enumerate(movie_list)
        ])

    @staticmethod
    def build_top_movie_embed(movie_list: list[Movie]) -> str:
        return '\n'.join([
            f"{i + 1}. [{movie.name} ({movie.year})]({movie.construct_url()}) - {movie.reaction_count}"
            for i, movie in enumerate(movie_list)
        ])


async def setup(bot: MoobieTime):
    await bot.add_cog(UserCog(bot))
