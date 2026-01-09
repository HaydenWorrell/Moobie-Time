from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class ConfigBase(Base):
    guild_id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    __tablename__ = f'config_{guild_id}'
    target_channel: Mapped[int] = mapped_column(Integer())
    suggest_channel: Mapped[int] = mapped_column(Integer())
    admin_role: Mapped[int] = mapped_column(Integer())

    def __repr__(self):
        return (
            f"target_channel={self.target_channel}, "
            f"suggest_channel={self.suggest_channel}, "
            f"admin_role={self.admin_role}, "
            f"guild_id={self.guild_id}",
        )
