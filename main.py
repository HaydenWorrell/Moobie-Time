import json
from pathlib import Path

import tvdb_v4_official

from moobie_time import MoobieTime
from config.config import Config
from searcher import SearchBoi

def main(config: Config):
    bot = MoobieTime(config)
    bot.run(config)


if __name__ == "__main__":


    f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
    config = Config(**json.loads(f))
    tvdb = tvdb_v4_official.TVDB(config.tvdb_key)
    movie_search = SearchBoi()
    movie = movie_search.search(movie_name='The Avengers')
    movie_str = movie.__repr__()
    movie_url = movie.construct_url()

    movie_base = movie.to_db(1, 2, 3)

    movie_base_str = movie_base.__repr__()

    main()
