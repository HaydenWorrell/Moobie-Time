from logging import getLogger
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from data.movie_entry import MovieBase

log = getLogger(__name__)


class Database:
    def __init__(self, path: Path) -> None:
        self.engine = create_engine(f'sqlite:///{path}')

    def add(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.id == movie.id)

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

    def remove(self, movie_name: str) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.name.like(f"%{movie_name}%"))

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
            slct = select(MovieBase).where(MovieBase.id == movie.id)

            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False

            existing_movie.reaction_count = movie.reaction_count
            session.commit()

            return True

    def from_message(self, message_id: int) -> MovieBase | None:
        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.message_id == message_id)
                if result := session.execute(slct).scalars().first():
                    return result
                log.warning(f"Failed to find suggestion in database with message id {message_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with message id {message_id}")

        return None

    def from_movie_id(self, movie_id: str) -> MovieBase | None:

        with Session(self.engine) as session:
            try:
                slct = select(MovieBase).where(MovieBase.id == movie_id)
                if result := session.execute(slct).scalars().first():
                    return result
                log.warning(f"Failed to find suggestion in database with movie id {movie_id}")

            except SQLAlchemyError:
                log.exception(f"Failed to find suggestion in database with movie id {movie_id}")

        return None

    def get_top_movies(self, count) -> list[MovieBase]:
        with Session(self.engine) as session:
            slct = (
                select(MovieBase)
                .where(MovieBase.watched == False)
                .order_by(MovieBase.reaction_count.desc())
                .limit(count)
            )
            results: list[MovieBase] = list(session.execute(slct).scalars().all())
            return results

    def mark_watched(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id)
            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False
            existing_movie.watched = True
            session.commit()
            return True

    def mark_unwatched(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            slct = select(MovieBase).where(MovieBase.id == movie.id)
            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False
            log.info(f"existing_movie.watched = {existing_movie.watched}, movie name: {existing_movie.name}")
            existing_movie.watched = False
            log.info(f"existing_movie.watched = {existing_movie.watched}, movie name: {existing_movie.name}")
            session.commit()
            return True
