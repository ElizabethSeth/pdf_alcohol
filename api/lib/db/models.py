from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "private_data"
    __table_args__ = {'schema': 'data'}

    id_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_unique: Mapped[str] = mapped_column(String(255))
    login_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
