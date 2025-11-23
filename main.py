import json
from pathlib import Path

import tvdb_v4_official

from moobie_time import MoobieTime
from config.config import Config



def main(config: Config):
    bot = MoobieTime(config)
    bot.run(config)


if __name__ == "__main__":


    f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
    config = Config(**json.loads(f))
    db = tvdb_v4_official.TVDB(config.tvdb_key)
    movie_list = db.search('The Avengers')
    movie_1 = movie_list[0]
    movie_1_id = movie_1["tvdb_id"]

    movie_url = "https://www.thetvdb.com/movies/" + movie_1["slug"]
    main()
