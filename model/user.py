from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger

from .meta import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    photo: Mapped[str]
    username: Mapped[str]
    age: Mapped[int]
    gender: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    filter_by_age: Mapped[str] = mapped_column(nullable=True)
    filter_by_gender: Mapped[str]
    filter_by_description: Mapped[str] = mapped_column(nullable=True)
    photo_i: Mapped[str]
