
from fastapi import FastAPI
from fastapi.params import Depends
from pydantic import BaseModel
from sqlalchemy import Column, String , Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from typing import Generator, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from sqlalchemy import create_engine
import lib.config as conf
app = FastAPI()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "private_data"
    __table_args__ = {'schema': 'data'}

    id_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_unique: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    login_time: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now(timezone.utc))

class LoginRequest(BaseModel):
    email: str
    password: str
    consent: bool | None = None

def init_db() -> None:
    Base.metadata.create_all(bind=conf.engine)

def get_db() -> Generator[Session, None, None]:
    db = conf.SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

def get_user_by_email(db: Session, email: str, password_unique: str):
    stmt = select(User).where(User.email == email, User.password_unique == password_unique)
    return db.execute(stmt).scalar_one_or_none() is not None

@app.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return True
    # print("login attempt:", payload.email)
    # return get_user_by_email(db=db, email=payload.email, password_unique=payload.password)

