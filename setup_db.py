from sqlalchemy import create_engine
from local_db.object import Base
from paths import Paths
import os

os.makedirs(Paths.OBJECT_FRAMES, exist_ok=True)
os.makedirs(Paths.RECORD_DATA_DIR, exist_ok=True)
engine = create_engine("sqlite:///objects.db", echo=True)
Base.metadata.create_all(engine)
