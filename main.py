import json
from pathlib import Path

from dotenv import load_dotenv
from os import environ
from moobie_time import MoobieTime
from moobie_time.config.config import Config


def main(config: Config):
    bot = MoobieTime(config)
    bot.run(config)


if __name__ == "__main__":
    with open(Path(__file__).parent / "config" / "config.json", "r") as f:
        config = Config(**json.loads(f))
    main()
