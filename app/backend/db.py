from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Dialect+driver://username:password@host:port/database
engine = create_engine('sqlite:///commerce.db', echo=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    ...
