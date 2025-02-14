from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class Object(Base):
    __tablename__ = "objects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    frame_path = Column(String, nullable=True)
    date_created = Column(DateTime, default=datetime.now())
    in_frame = Column(JSON, nullable=True)

    records = relationship(
        "ObjectRecord",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        name="",
        frame_path="",
        in_frame=None,
        date_created=None,
    ):
        self.name = name
        self.frame_path = frame_path
        self.date_created = date_created or datetime.now()
        self.in_frame = in_frame if in_frame else []


class ObjectRecord(Base):
    __tablename__ = "object_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    file_path = Column(String, nullable=False)
    date_uploaded = Column(DateTime, default=datetime.now())
    is_processed = Column(Boolean, default=False)
    parent = relationship("Object", back_populates="records")

    def __init__(self, file_path="", date_uploaded=None):
        self.file_path = file_path
        self.date_uploaded = date_uploaded or datetime.now()
