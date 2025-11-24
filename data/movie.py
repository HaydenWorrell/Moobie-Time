from logging import getLogger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel

from data.movie_entry import MovieBase

log = getLogger(__name__)


class Movie(BaseModel):
    id: str
    name: str
    image: str
    year: str
    slug: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, image={self.image}, year={self.year}, slug={self.slug})"

    def construct_url(self) -> str:
        url = "https://www.thetvdb.com/movies/" + str(self.slug)
        return url

    def to_db(self, requester_id: int = 0, reaction_count: int = 0, message_id: int = 0) -> MovieBase:
        return MovieBase(
            id=self.id,
            name=self.name,
            link=self.construct_url(),
            requester=requester_id,
            reaction_count=reaction_count,
            message_id=message_id
        )
