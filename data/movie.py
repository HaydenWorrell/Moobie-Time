from logging import getLogger
from typing import Annotated

import discord
from pydantic import BaseModel, ConfigDict, Field

from data.movie_entry import MovieBase

log = getLogger(__name__)


# class Alias(BaseModel):
#


class Movie(BaseModel):
    model_config = ConfigDict(extra='ignore')
    tvdb_id: str
    name: str
    image: str | None = None
    year: str | None
    slug: str
    reaction_count: int | None = None
    aliases: Annotated[list[str], Field(default_factory=list)]
    watched: bool | None = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.tvdb_id}, name={self.name}, image={self.image}, year={self.year}, slug={self.slug}, reaction_count={self.reaction_count})"

    def __str__(self) -> str:
        return self.name

    def construct_url(self) -> str:
        url = "https://www.thetvdb.com/movies/" + str(self.slug)
        return url

    def to_db(self, requester_id: int = 0, reaction_count: int = 0, message_id: int = 0) -> MovieBase:
        return MovieBase(
            id=self.tvdb_id,
            name=self.name,
            link=self.construct_url(),
            requester=requester_id,
            reaction_count=reaction_count,
            message_id=message_id,
            watched=self.watched,
            year=self.year,
            slug=self.slug,
        )

    def to_embed(self):
        return discord.Embed(
            title=f"{self.name} ({self.year})",
            url=self.construct_url(),
            color=discord.Color.green(),
        )

    @staticmethod
    def from_db(movie_base: MovieBase) -> Movie:
        return Movie(
            tvdb_id=movie_base.id,
            name=movie_base.name,
            image='',
            year=movie_base.year,
            slug=movie_base.slug,
            reaction_count=movie_base.reaction_count,
            aliases=None,
            watched=movie_base.watched,
        )
