import json
from logging import getLogger
from pathlib import Path
from typing import Any

import tvdb_v4_official
from discord.ext import commands
from pydantic import ValidationError

from config.config import Config
from data.movie import Movie

log = getLogger(__name__)

f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
config = Config(**json.loads(f))

tvdb = tvdb_v4_official.TVDB(config.tvdb_key)


class SearchBoi(commands.Cog):
    def __init__(self) -> None:
        self.db = tvdb_v4_official.TVDB(config.tvdb_key)

    def search(self, movie_name: str, length: int = 5) -> list[Movie]:
        search_term = ''.join(char for char in movie_name if char.isalnum() or char.isspace())
        movie_list = self.db.search(search_term)

        movie_obj_list = [movie for mov in movie_list[:length] if (movie := self.build_movie(mov))]

        return movie_obj_list

    def search_with_year(self, movie_name: str, year: str, length: int = 5, watched: bool = False) -> list[Movie]:
        search_term = ''.join(char for char in movie_name if char.isalnum() or char.isspace())
        movie_list = self.db.search(search_term, year=year)

        movie_obj_list = [movie for mov in movie_list[:length] if (movie := self.build_movie(mov, watched=watched))]

        return movie_obj_list

    @staticmethod
    def build_movie(movie: dict[str, Any], watched: bool = False) -> Movie | None:
        try:
            if movie.get("type") != "movie":
                return None
            return Movie(**movie, watched=watched)

        except KeyError:
            log.exception(f"Failed to build movie from {movie.get('name', 'unknown')}")
            return None
        except ValidationError:
            log.exception(f"Failed to validate model from {movie}")
            return None
