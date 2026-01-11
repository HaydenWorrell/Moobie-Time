from logging import getLogger
from pathlib import Path

# from .db_schema import ConfigBase
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from data.db_schema import ConfigBase, GuildMovieEntry, MovieBase

log = getLogger(__name__)


class Database:
    def __init__(self, path: Path) -> None:
        self.engine = create_engine(f'sqlite:///{path}')

    def add(self, movie: MovieBase, guild_id: int, message_id: int) -> bool:
        with Session(self.engine) as session:
            try:
                if not session.get(MovieBase, movie.id):
                    session.add(movie)

                if session.get(GuildMovieEntry, (movie.id, guild_id)):
                    log.warning(
                        f"Movie {movie.id} already exists in database with name {movie.name} for guild id {guild_id}"
                    )
                    return False

                session.add(
                    GuildMovieEntry(
                        name=movie.name,
                        guild_id=guild_id,
                        movie_id=movie.id,
                        message_id=message_id,
                    )
                )

                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to add {movie.name} to database with error \n")
                session.rollback()
                return False

        return True

    def remove(self, movie_name: str, guild_id: int) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(GuildMovieEntry).where(
                    GuildMovieEntry.name.like(f"%{movie_name}%"), (GuildMovieEntry.guild_id == guild_id)
                )

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

    def update_reactions(self, movie: GuildMovieEntry, guild_id: int) -> bool:
        with Session(self.engine) as session:
            if not (existing_movie := session.get(GuildMovieEntry, (movie.movie_id, guild_id))):
                log.warning(f"Movie {movie.movie_id} does not exist in database with name {movie.name}")
                return False

            existing_movie.reaction_count = movie.reaction_count
            session.commit()

            return True

    def from_message(self, message_id: int, guild_id: int) -> GuildMovieEntry | None:
        with Session(self.engine) as session:
            try:
                slct = select(GuildMovieEntry).where(
                    GuildMovieEntry.message_id == message_id, GuildMovieEntry.guild_id == guild_id
                )
                if result := session.execute(slct).scalars().first():
                    return result
                log.warning(f"Failed to find suggestion in database with message id {message_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with message id {message_id}")

        return None

    def from_movie_id(self, movie_id: str, guild_id: int) -> GuildMovieEntry | None:

        with Session(self.engine) as session:
            try:
                if result := session.get(GuildMovieEntry, (movie_id, guild_id)):
                    return result
                log.warning(f"Failed to find suggestion in database with movie id {movie_id} and guild id {guild_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with movie id {movie_id}")

        return None

    def get_top_movies(self, count: int, guild_id: int) -> list[tuple[MovieBase, int]] | None:
        with Session(self.engine) as session:
            slct = (
                select(GuildMovieEntry)
                .where(GuildMovieEntry.watched == False, GuildMovieEntry.guild_id == guild_id)
                .order_by(GuildMovieEntry.reaction_count.desc())
                .limit(count)
            )
            results: list[tuple[MovieBase, int]] = [
                (entry.movie, entry.reaction_count) for entry in session.execute(slct).scalars().all()
            ]
            return results

    def mark_watched(self, movie: GuildMovieEntry, guild_id: int) -> bool:
        with Session(self.engine) as session:
            if not (existing_movie := session.get(GuildMovieEntry, (movie.movie_id, guild_id))):
                log.warning(
                    f"Movie {movie.movie_id} does not exist in database with name {movie.name} for guild {guild_id}"
                )
                return False
            existing_movie.watched = True
            session.commit()
            return True

    def mark_unwatched(self, movie: GuildMovieEntry, guild_id: int) -> bool:
        with Session(self.engine) as session:
            if not (existing_movie := session.get(GuildMovieEntry, (movie.movie_id, guild_id))):
                log.warning(f"Movie {movie.movie_id} does not exist in database with name {movie.name}")
                return False
            existing_movie.watched = False
            session.commit()
            return True

    # def update_message_id(self, movie: MovieBase, message_id: int) -> bool:
    #     with Session(self.engine) as session:
    #         slct = select(MovieBase).where(MovieBase.id == movie.id, MovieBase.guild_id == movie.guild_id)
    #         if not (existing_movie := session.execute(slct).scalars().first()):
    #             log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
    #             return False
    #         log.info(f"existing_movie.message_id = {existing_movie.message_id}, movie name: {existing_movie.name}")
    #         existing_movie.message_id = message_id
    #         log.info(f"existing_movie.message_id = {existing_movie.message_id}, movie name: {existing_movie.name}")
    #         session.commit()
    #         return True

    def config_from_id(self, guild_id: int) -> ConfigBase | None:
        with Session(self.engine) as session:
            try:
                return session.get(ConfigBase, guild_id)
            except SQLAlchemyError:
                log.exception(f"Failed to find config for guild {guild_id}")
            return None
