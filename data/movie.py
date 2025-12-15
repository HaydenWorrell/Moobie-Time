from logging import getLogger

import discord
from pydantic import BaseModel

from data.movie_entry import MovieBase

log = getLogger(__name__)


class Movie(BaseModel):
    id: str
    name: str
    image: str
    year: str
    slug: str
    reaction_count: int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, image={self.image}, year={self.year}, slug={self.slug}, reaction_count={self.reaction_count})"

    def construct_url(self) -> str:
        url = "https://www.thetvdb.com/movies/" + str(self.slug)
        return url

    def to_db(
        self, requester_id: int = 0, reaction_count: int = 0, message_id: int = 0, watched_yet: bool = False
    ) -> MovieBase:
        return MovieBase(
            id=self.id,
            name=self.name,
            link=self.construct_url(),
            requester=requester_id,
            reaction_count=reaction_count,
            message_id=message_id,
            watched=watched_yet,
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
            id=movie_base.id,
            name=movie_base.name,
            image='',
            year=movie_base.year,
            slug=movie_base.slug,
            reaction_count=movie_base.reaction_count,
        )
