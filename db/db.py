from PyQt6.QtSql import QSqlDatabase
from sqlalchemy import create_engine
from db.object import Base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///objects.db", echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    """Creates and returns a new session."""
    return Session()
