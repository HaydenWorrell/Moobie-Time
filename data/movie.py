from logging import getLogger

from pydantic import BaseModel

log = getLogger(__name__)

class Movie(BaseModel):
    id: str
    name: str
    image: str
    year: str
