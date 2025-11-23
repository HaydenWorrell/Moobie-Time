import json
from logging import getLogger
from pathlib import Path

import tvdb_v4_official

from discord.ext import commands

from config.config import Config
from data.movie import Movie


log = getLogger(__name__)

f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
config = Config(**json.loads(f))

tvdb = tvdb_v4_official.TVDB(config.tvdb_key)

class SearchBoi(commands.Cog):
    def __init__(self) -> None:
        self.db = tvdb_v4_official.TVDB(config.tvdb_key)


    def search(self, movie_name: str) -> Movie:
        movie_list = self.db.search(movie_name)
        top_result = movie_list[0]

        movie_id: str = top_result["tvdb_id"]
        movie_name: str = top_result["name"]
        movie_image: str = top_result["image_url"]
        movie_year: str = top_result["year"]
        movie_slug: str = top_result["slug"]

        movie_obj = Movie(id=movie_id, name=movie_name, image=movie_image, year=movie_year, slug=movie_slug)

        return movie_obj



