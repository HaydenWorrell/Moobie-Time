from __future__ import annotations

import discord
from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MovieBase(Base):
    __tablename__ = "movies"
    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    link: Mapped[str] = mapped_column(String())
    slug: Mapped[str] = mapped_column(String())
    year: Mapped[str] = mapped_column(String())

    watch_list: Mapped[list[GuildMovieEntry]] = relationship(back_populates="movie")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name}, "
            f"link={self.link}, "
            f"slug={self.slug}, "
            f"year={self.year})"
        )

    def __str__(self) -> str:
        return f"{self.name}: ({self.year})"

    def to_embed(self):
        return discord.Embed(
            title=f"{self.name} ({self.year})",
            url=self.link,
            color=discord.Color.green(),
        )


class GuildBase(Base):
    __tablename__ = "guilds"
    guild_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)

    watch_list: Mapped[list[GuildMovieEntry]] = relationship(back_populates="guild")
    config: Mapped[ConfigBase] = relationship(back_populates="guild")


class GuildMovieEntry(Base):
    __tablename__ = "guild_movie_list"
    reaction_count: Mapped[int] = mapped_column(BigInteger(), default=0)
    message_id: Mapped[int] = mapped_column(BigInteger(), default=0)
    watched: Mapped[bool] = mapped_column(Boolean(), default=False)
    name: Mapped[str] = mapped_column(String(), default=None)

    # relational info

    movie_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("movies.id"),
        primary_key=True,
    )

    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("guilds.guild_id"),
        primary_key=True,
    )
    guild: Mapped[GuildBase] = relationship(back_populates="watch_list")
    movie: Mapped[MovieBase] = relationship(back_populates="watch_list")


class ConfigBase(Base):
    __tablename__ = "config"
    target_channel: Mapped[int] = mapped_column(BigInteger())
    suggest_channel: Mapped[int] = mapped_column(BigInteger())
    admin_role: Mapped[int] = mapped_column(BigInteger())
    guild_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("guilds.guild_id"),
        primary_key=True,
    )

    guild: Mapped[GuildBase] = relationship(back_populates="config")
