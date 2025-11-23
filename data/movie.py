from logging import getLogger

from pydantic import BaseModel

log = getLogger(__name__)

class Movie(BaseModel):
    id: str
    name: str
    image: str
    year: str
    slug: str

    async def construct_url(self) -> str:

        url = "https://www.thetvdb.com/movies/" + str(self.slug)
        return url