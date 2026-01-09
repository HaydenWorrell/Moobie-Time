from logging import getLogger
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.config_base import ConfigBase
from data.movie_entry import MovieBase

log = getLogger(__name__)


class Database:
    def __init__(self, path: Path) -> None:
        self.engine = create_engine(f'sqlite:///{path}')

    def add(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)

                if existing_movie := session.execute(slct).scalars().first():
                    log.warning(f"Movie {movie.id} already exists in database with name {existing_movie.name}")
                    return False

                session.add(movie)
                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to add {movie.name} to database with error \n")
                session.rollback()
                return False

        return True

    def remove(self, movie_name: str, guild_id: int) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.name.like(f"%{movie_name}%"), (MovieBase.guild_id == guild_id))

                if not (existing_movie := session.execute(slct).scalars().first()):
                    log.warning(f"Movie does not exist in database with name: {movie_name}")
                    return False

                session.delete(existing_movie)
                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to remove {movie_name} from database with error \n")
                session.rollback()
                return False

        return True

    def add_batch(self, movies: list[MovieBase]) -> int:
        count = 0

        for movie in movies:
            if self.add(movie):
                count += 1

        return count

    def update_reactions(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)

            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False

            existing_movie.reaction_count = movie.reaction_count
            session.commit()

            return True

    def from_message(self, message_id: int, guild_id: int) -> MovieBase | None:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.message_id == message_id, MovieBase.guild_id == guild_id)
                if result := session.execute(slct).scalars().first():
                    return result
                log.warning(f"Failed to find suggestion in database with message id {message_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with message id {message_id}")

        return None

    def from_movie_id(self, movie_id: str, guild_id: int) -> MovieBase | None:

        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.id == movie_id, MovieBase.guild_id == guild_id)
                if result := session.execute(slct).scalars().first():
                    return result
                log.warning(f"Failed to find suggestion in database with movie id {movie_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with movie id {movie_id}")

        return None

    def get_top_movies(self, count: int, guild_id: int) -> list[MovieBase]:
        with Session(self.engine) as session:
            slct = (
                select(MovieBase)
                .where(MovieBase.watched == False, MovieBase.guild_id == guild_id)
                .order_by(MovieBase.reaction_count.desc())
                .limit(count)
            )
            results: list[MovieBase] = list(session.execute(slct).scalars().all())
            return results

    def mark_watched(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)
            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False
            existing_movie.watched = True
            session.commit()
            return True

    def mark_unwatched(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)
            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False
            log.info(f"existing_movie.watched = {existing_movie.watched}, movie name: {existing_movie.name}")
            existing_movie.watched = False
            log.info(f"existing_movie.watched = {existing_movie.watched}, movie name: {existing_movie.name}")
            session.commit()
            return True

    def update_message_id(self, movie: MovieBase, message_id: int) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)
            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False
            log.info(f"existing_movie.message_id = {existing_movie.message_id}, movie name: {existing_movie.name}")
            existing_movie.message_id = message_id
            log.info(f"existing_movie.message_id = {existing_movie.message_id}, movie name: {existing_movie.name}")
            session.commit()
            return True

    def check_admin_role(self, role_id: int, guild_id: int) -> bool:
        with Session(self.engine) as session:
            slct = select(ConfigBase).where(ConfigBase.admin_role == role_id, ConfigBase.guild_id == guild_id)
            if not (existing_role := session.execute(slct).scalars().first()):
                log.info(f"Admin role check returned false, Role ID: {role_id}")
                return False
            return True

    def check_target_channel(self, channel_id: int, guild_id: int) -> bool:
        with Session(self.engine) as session:
            slct = select(ConfigBase).where(ConfigBase.target_channel == channel_id, ConfigBase.guild_id == guild_id)
            if not (existing_channel := session.execute(slct).scalars().first()):
                log.info(f"Target channel not found, channel id: {channel_id}, guild id: {guild_id}")
                return False
            return True
