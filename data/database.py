from logging import getLogger
from pathlib import Path


from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from moobie_time.data.movie import Movie

log = getLogger(__name__)
class Database:
    def __init__(self, path: Path) -> None:
        self.engine = create_engine(f'sqlite:///{path}')

    def add(self, movie: Movie) -> bool:
        with Session(self.engine) as session:
            try:
                slct = select(Movie).where(Movie.id == movie.id)

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

    def remove(self, movie: Movie) -> bool:
        with Session(self.engine) as session:
            try:
                session.delete(movie)
                session.commit()
            except SQLAlchemyError:
                log.exception(f"Failed to remove {movie.name} from database with error \n")
                session.rollback()
                return False

        return True

    def add_batch(self, movies: list[Movie]) -> int:
        count = 0

        for movie in movies:
            if self.add(movie): count += 1

        return count

    def update_reactions(self, movie: Movie) -> bool:
        with Session(self.engine) as session:
            slct = select(Movie).where(Movie.id == movie.id)

            if not (existing_movie := session.execute(slct).scalars().first()):
                log.warning(f"Movie {movie.id} does not exist in database with name {movie.name}")
                return False

            existing_movie.reaction_count = movie.reaction_count
            session.commit()

            return True



