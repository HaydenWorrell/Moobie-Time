from logging import getLogger

from pydantic import BaseModel

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

