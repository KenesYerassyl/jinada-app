from sqlalchemy import create_engine
from object import Base

engine = create_engine("sqlite:///objects.db", echo=True)
Base.metadata.create_all(engine)
