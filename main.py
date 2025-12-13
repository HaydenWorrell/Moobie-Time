import json
from pathlib import Path

import tvdb_v4_official

from moobie_time import MoobieTime
from config.config import Config
from data.movie_entry import Base


def main(config: Config):
    bot = MoobieTime(config)
    Base.metadata.create_all(bind=bot.database.engine)
    bot.run(config.token)


if __name__ == "__main__":
    f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
    config = Config(**json.loads(f))

    tvdb = tvdb_v4_official.TVDB(config.tvdb_key)

    main(config)
