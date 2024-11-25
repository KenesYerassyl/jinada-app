import cv2
import os
import time
import json
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class Object(Base):
    __tablename__ = "objects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    frame_path = Column(String, nullable=True)
    date_created = Column(DateTime, default=time.strftime("%Y-%m-%d %H:%M"))
    in_frame = Column(JSON, nullable=True)
    out_frame = Column(JSON, nullable=True)

    records = relationship(
        "ObjectRecord", backref="object", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        name,
        frame_path="",
        in_frame=None,
        out_frame=None,
        date_created=None,
    ):
        self.name = name
        self.frame_path = frame_path
        self.date_created = (
            date_created
            if date_created
            else time.strftime("%Y-%m-%d %H:%M", time.localtime())
        )
        self.in_frame = in_frame if in_frame else []
        self.out_frame = out_frame if out_frame else []

    def save_first_frame(self):
        result = ()
        file_name, _ = os.path.splitext(os.path.basename(self.file_path))
        output_image_path = os.path.join(
            os.path.dirname(self.file_path), f"{file_name}.jpg"
        )
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"Video file not found: {self.file_path}")

            cap = cv2.VideoCapture(self.file_path)
            if not cap.isOpened():
                raise IOError(f"Error: Cannot open video file: {self.file_path}")

            success, frame = cap.read()
            if not success:
                raise ValueError("Error: Could not read the first frame of the video")

            cv2.imwrite(output_image_path, frame)
            self.set_frame_path(output_image_path)
            result = (1, f"First frame saved successfully to {output_image_path}")

        except FileNotFoundError as fnf_error:
            result = (0, repr(fnf_error))
        except IOError as io_error:
            result = (0, repr(io_error))
        except ValueError as val_error:
            result = (0, repr(val_error))
        except Exception as e:
            result = (0, repr(f"An unexpected error occurred: {e}"))
        finally:
            if "cap" in locals() and cap.isOpened():
                cap.release()
        return result


class ObjectRecord(Base):
    __tablename__ = "object_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    file_path = Column(String, nullable=False)
    date_uploaded = Column(DateTime, default=time.strftime("%Y-%m-%d %H:%M"))

    def __init__(self, file_path, date_uploaded):
        self.file_path = file_path
        self.date_uploaded = (
            date_uploaded
            if date_uploaded
            else time.strftime("%Y-%m-%d %H:%M", time.localtime())
        )
