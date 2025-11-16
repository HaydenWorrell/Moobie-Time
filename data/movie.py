from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



class Base(DeclarativeBase):
    pass
class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    requester: Mapped[int] = mapped_column()
    reaction_count: Mapped[int] = mapped_column(count=0)
    message_id: Mapped[int] = mapped_column()
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, requester={self.requester})"

    def __str__(self) -> str:
        return f"{self.name}"

