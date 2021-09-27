from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import DSN, DSNTEST

Base = declarative_base()
engine = create_engine(DSN)
test_engine = create_engine(DSNTEST)
Session = sessionmaker(bind=engine)
DBSession = Session()


class Database:
    def __init__(self, session: DBSession):
        self.session = session




