import json
from logging import getLogger
from pathlib import Path
from typing import Any

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


    def search(self, movie_name: str) -> list[Movie]:
        search_term = ''.join(char for char in movie_name if char.isalnum() or char.isspace())
        movie_list = self.db.search(search_term)

        movie_obj_list = [movie for mov in movie_list[:5] if (movie := self.build_movie(mov))]


        return movie_obj_list

    @staticmethod
    def build_movie(movie: dict[str, Any]) -> Movie|None:
        try:
            movie_id: str = movie["tvdb_id"]
            movie_name: str = movie["name"]
            movie_image: str = movie["image_url"]
            movie_year: str = movie["year"]
            movie_slug: str = movie["slug"]

            return Movie(id=movie_id, name=movie_name, image=movie_image, year=movie_year, slug=movie_slug)

        except KeyError:
            log.error(f"Failed to build movie from {movie.get('name', 'unknown')}")


