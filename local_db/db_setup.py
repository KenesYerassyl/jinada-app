from sqlalchemy import create_engine
from object import Base
import os

os.makedirs("./local_db/object_frames", exist_ok=True)
engine = create_engine("sqlite:///objects.db", echo=True)
Base.metadata.create_all(engine)
