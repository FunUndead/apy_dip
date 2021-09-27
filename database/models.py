from sqlalchemy import (
    Column,
    Integer
)
from database.base import Base, engine, test_engine


class User(Base):
    __tablename__ = 'userdata'
    user_id = Column(Integer, primary_key=True)
    age = Column(Integer)
    sex = Column(Integer)
    city = Column(Integer)
    relation = Column(Integer)


class Matches(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    match_id = Column(Integer)
    seen = Column(Integer)

Base.metadata.create_all(test_engine)
Base.metadata.create_all(engine)