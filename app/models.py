from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

from .database import Base

class Subscription_DB(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    asset_name: Mapped[str] = mapped_column(String(5))
    target_price: Mapped[float] = mapped_column(nullable=False)
    is_alerted: Mapped[bool] = mapped_column(default=False)
    #RESTRICT - prevents deletion users if that has subs
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    owner: Mapped["User_DB"] = relationship(back_populates="subscriptions")


class User_DB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    
    subscriptions: Mapped[list["Subscription_DB"]] = relationship(back_populates="owner", cascade="all, delete-orphan")



