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

                if existing_movie:= session.execute(slct).scalars().first():
                    log.warning(f"Movie {movie.id} already exists in database with name {existing_movie.name}")
                    return False

                session.add(movie)
                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to add {movie.name} to database with error \n")
                session.rollback()
                return False

        return True

    def remove(self, movie: MovieBase) -> bool:
        with Session(self.engine) as session:
            try:
                session.delete(movie)
                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to remove {movie.name} from database with error \n")
                session.rollback()
                return False

        return True

    def add_batch(self, movies: list[MovieBase]) -> int:
        count = 0

        for movie in movies:
            if self.add(movie): count += 1

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



