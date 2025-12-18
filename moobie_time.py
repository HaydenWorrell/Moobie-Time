import logging
from asyncio import sleep
from pathlib import Path

import discord
from async_property import async_cached_property
from discord import TextChannel
from discord.ext import commands

from config.config import Config
from data.database import Database
from data.movie import Movie

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
discord.utils.setup_logging()
discord.utils.setup_logging(level=logging.DEBUG, root=False)
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True


class MoobieTime(commands.Bot):
    def __init__(self, config: Config):
        self.config: Config = config
        path = Path(__file__).parent / config.database_path
        self.database = Database(path)

        super().__init__(
            intents=INTENTS,
            command_prefix=commands.when_mentioned_or("&"),
            allowed_mentions=discord.AllowedMentions(everyone=False),
        )

    @property
    def prefix(self):
        return self.config.prefix

    @async_cached_property
    async def movie_channel(self) -> TextChannel | None:
        return await self.fetch_channel(int(self.config.target_channel))

    async def setup_hook(self):
        # add cogs
        for cog in self.config.cogs:
            await self.load_extension(cog)

        # sync all commands
        synced = await self.tree.sync()
        log.info(f"Added main cog commands... Synced {len(synced)} commands")

    async def reload_extensions(self) -> list[str]:
        ext_count: int = len(self.extensions)
        log.info(f"Attempting to reload {ext_count} extensions...")
        pre_reload_exts = list(self.extensions)

        for ext in pre_reload_exts:
            await self.reload_extension(ext)
        await sleep(1)
        return list(self.extensions)

    @staticmethod
    def log_action(ctx: commands.Context, message: str):
        log.info(f"{ctx.author.name}({ctx.author.id}): {message}")

    async def push_movie(self, ctx: commands.Context, movie: Movie):
        channel = await self.movie_channel
        if existing_movie := self.database.from_movie_id(movie.tvdb_id):
            existing_msg = await channel.fetch_message(existing_movie.message_id)
            await ctx.send(
                f"Could not add {movie.name} ({movie.year}) to the database, here's the link to the message: "
                f"{existing_msg.jump_url} "
                f"Heart react to upvote it!",
                ephemeral=True,
            )
            return
        else:
            message = await channel.send(embed=movie.to_embed())
            await message.add_reaction('💖')
            movie_obj = movie.to_db(message_id=message.id)

            if self.database.add(movie_obj):
                await ctx.send(
                    f"Successfully added {movie.name} ({movie.year}) to the database",
                    ephemeral=True,
                )

            else:
                await ctx.send(
                    f"Could not add {movie.name} to the database",
                    ephemeral=True,
                )


async def permissions_check(ctx: commands.Context) -> bool:
    if any(role for role in ctx.author.roles if role.id == ctx.bot.config.admin_role):
        return True

    await ctx.reply("You do not have permissions to use this command.", ephemeral=True)
    log.warning(f"{ctx.author.name}({ctx.author.id}): attempted to use {ctx.command}")
    return False
