import json
from pathlib import Path

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declarative_base
from sqlalchemy import String, Integer, create_engine

from config.config import Config


class Base(DeclarativeBase):
    pass



class MovieBase(Base):
    __tablename__ = "movies"
    id: Mapped[str] = mapped_column(String(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    link: Mapped[str] = mapped_column(String())
    requester: Mapped[int] = mapped_column(Integer())
    reaction_count: Mapped[int] = mapped_column(Integer())
    message_id: Mapped[int] = mapped_column(Integer())



    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, link={self.link}, requester={self.requester}, reaction_count={self.reaction_count}, message_id={self.message_id})"

    def __str__(self) -> str:
        return f"{self.name}"
