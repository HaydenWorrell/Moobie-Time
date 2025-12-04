import json
from pathlib import Path

import tvdb_v4_official
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from moobie_time import MoobieTime
from config.config import Config

Base = declarative_base()
def main(config: Config):
    bot = MoobieTime(config)
    Base.metadata.create_all(bot.database.engine)
    bot.run(config.token)

if __name__ == "__main__":


    f = (Path(__file__).parent / "config" / "config.json").read_text(encoding="utf-8-sig")
    config = Config(**json.loads(f))

    tvdb = tvdb_v4_official.TVDB(config.tvdb_key)

    main(config)
