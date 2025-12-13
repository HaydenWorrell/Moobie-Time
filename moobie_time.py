import logging
from asyncio import sleep
from pathlib import Path

import discord
from discord.ext import commands

from config.config import Config
from data.database import Database

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
            allowed_mentions=discord.AllowedMentions(everyone=False)
        )

    @property
    def prefix(self):
        return self.config.prefix

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


async def permissions_check(ctx: commands.Context) -> bool:
    if any(role for role in ctx.author.roles if role.id == ctx.bot.config.admin_role):
        return True

    await ctx.reply(f"You do not have permissions to use this command.", ephemeral=True)
    log.warning(f"{ctx.author.name}({ctx.author.id}): attempted to use {ctx.command}")
    return False
