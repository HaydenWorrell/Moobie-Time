import json
from logging import getLogger
from pathlib import Path

import imdb
import tvdb_v4_official
from imdb.Movie import Movie as IMDbMovie

from discord.ext import commands

from config.config import Config
from data.movie_entry import MovieBase
from moobie_time import MoobieTime

log = getLogger(__name__)

f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
config = Config(**json.loads(f))

tvdb = tvdb_v4_official.TVDB(config.tvdb_key)

class SearchBoi(commands.Cog):
    def __init__(self) -> None:
        self.ia = imdb.Cinemagoer()


    async def search(self, movie_name: str) -> None:
        pass


