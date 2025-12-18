import discord
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    watched: Mapped[bool] = mapped_column(Boolean())
    slug: Mapped[str] = mapped_column(String())
    year: Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name}, "
            f"link={self.link}, "
            f"requester={self.requester}, "
            f"reaction_count={self.reaction_count}, "
            f"message_id={self.message_id}, "
            f"watched={self.watched}, "
            f"slug={self.slug}, "
            f"year={self.year})"
        )

    def __str__(self) -> str:
        return f"{self.name}"

    def to_embed(self):
        return discord.Embed(
            title=f"{self.name} ({self.year})",
            url=self.link,
            color=discord.Color.green(),
        )
