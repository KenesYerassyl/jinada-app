import logging
from typing import List, Tuple
from sqlalchemy import create_engine
from db.object import Base, Object, ObjectRecord
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.db_fs import delete_file
from sqlalchemy.orm import joinedload
from paths import Paths, DB_PATH
import datetime


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error during session: {e}")
        raise
    finally:
        session.close()


def insert_object(object: Object) -> int:
    """
    Insert a new object into the database and return its ID.
    """
    try:
        with get_session() as session:
            session.add(object)
            session.flush()
            logging.info(f"Object inserted: {object.name} with ID {object.id}")
            return object.id
    except Exception as e:
        logging.error(f"Error inserting object {object}: {e}")
        raise


def insert_record(object_id: int, object_record: ObjectRecord) -> int:
    """
    Insert a new record into the database for the given object and return its ID.
    """
    try:
        with get_session() as session:
            obj = session.query(Object).options(joinedload(Object.records)).get(object_id)
            if obj is None:
                raise ValueError(f"Object with ID {object_id} not found.")
            object_record.parent = obj
            obj.records.append(object_record)
            session.add(object_record)
            session.flush()
            logging.info(f"Record inserted for object {object_id} with record ID {object_record.id}")
            return object_record.id
    except Exception as e:
        logging.error(f"Error inserting record: {e}")
        raise
    
def get_all_objects_for_list():
    """
    Retrieve a list of all objects for displaying in a list.
    """
    try:
        with get_session() as session:
            objects = session.query(Object.id, Object.name, Object.date_created).all()
            logging.info(f"Retrieved {len(objects)} objects.")
            return objects
    except Exception as e:
        logging.error(f"Error retrieving objects: {e}")
        raise

def get_all_records_for_list(object_id: int):
    """
    Retrieve all records associated with a specific object.
    """
    try:
        with get_session() as session:
            records = (
                session.query(
                    ObjectRecord.id,
                    ObjectRecord.file_path,
                    ObjectRecord.date_uploaded,
                    ObjectRecord.is_processed,
                )
                .join(ObjectRecord.parent)
                .filter(ObjectRecord.object_id == object_id)
                .all()
            )
            logging.info(f"Retrieved {len(records)} records for object ID {object_id}.")
            return records
    except Exception as e:
        logging.error(f"Error retrieving records for object {object_id}: {e}")
        raise

def get_records_for_export(object_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    Retrieve all records for a specific object ID within a date range.
    """
    try:
        # start_date = start_date.replace(hour=0, minute=0, second=0)
        # end_date = end_date.replace(hour=0, minute=0, second=0)
        with get_session() as session:
            results = (
                session.query(ObjectRecord.id)
                .filter(
                    ObjectRecord.object_id == object_id,
                    ObjectRecord.date_uploaded >= start_date,
                    ObjectRecord.date_uploaded <= end_date,
                    ObjectRecord.is_processed == True
                )
                .all()
            )
            results = [result[0] for result in results]
            return results

    except Exception as e:
        logging.error(f"Error retrieving records for object_id={object_id}: {e}")
        raise

def get_object_by_id(object_id: int):
    """
    Retrieve an object by its ID.
    """
    try:
        with get_session() as session:
            obj = session.query(Object).filter_by(id=object_id).first()
            if obj:
                logging.info(f"Object found: {obj.name}")
                return {
                    "id": obj.id,
                    "name": obj.name,
                    "date_created": obj.date_created,
                    "frame_path": obj.frame_path,
                    "in_frames": obj.in_frame,
                }
            else:
                logging.warning(f"Object with ID {object_id} not found.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving object {object_id}: {e}")
        raise

def get_record_by_id(record_id: int):
    """
    Retrieve a record by its ID.
    """
    try:
        with get_session() as session:
            record = session.query(ObjectRecord).filter_by(id=record_id).first()
            if record:
                logging.info(f"Record found for object {record.object_id}")
                return {
                    "id": record.id,
                    "object_id": record.object_id,
                    "file_path": record.file_path,
                    "date_uploaded": record.date_uploaded,
                    "is_processed": record.is_processed,
                }
            else:
                logging.warning(f"Record with ID {record_id} not found.")
                return None
    except Exception as e:
        logging.error(f"Error retrieving record {record_id}: {e}")
        raise

def update_object_by_id(object_id: int, name: str, in_frames: List[List[Tuple[int, int]]]):
    """
    Update the details of an object by its ID.
    """
    try:
        with get_session() as session:
            obj = session.query(Object).filter_by(id=object_id).first()
            if obj:
                obj.name = name
                obj.in_frame = in_frames
                logging.info(f"Object {object_id} updated.")
            else:
                logging.warning(f"Object with ID {object_id} not found.")
    except Exception as e:
        logging.error(f"Error updating object {object_id}: {e}")
        raise


def delete_object_by_id(object_id: int):
    """
    Delete an object by its ID along with its associated records.
    """
    try:
        with get_session() as session:
            obj = session.query(Object).filter_by(id=object_id).first()
            if obj:
                for record in obj.records:
                    delete_file(Paths.record_data_npz(record.id))
                delete_file(obj.frame_path)
                session.delete(obj)
                logging.info(f"Object with ID {object_id} and its records deleted.")
            else:
                logging.warning(f"Object with ID {object_id} not found.")
    except Exception as e:
        logging.error(f"Error deleting object {object_id}: {e}")
        raise


def update_record_status(record_id: int):
    """
    Update the status of a record to 'processed'.
    """
    try:
        with get_session() as session:
            record = session.query(ObjectRecord).filter_by(id=record_id).first()
            if record:
                record.is_processed = True
                logging.info(f"Record {record_id} marked as processed.")
            else:
                logging.warning(f"Record with ID {record_id} not found.")
    except Exception as e:
        logging.error(f"Error updating record {record_id}: {e}")
        raise


def delete_record_by_id(record_id: int):
    """
    Delete a record by its ID.
    """
    try:
        with get_session() as session:
            record = session.query(ObjectRecord).filter_by(id=record_id).first()
            if record:
                delete_file(Paths.record_data_npz(record.id))
                session.delete(record)
                logging.info(f"Record with ID {record_id} deleted.")
            else:
                logging.warning(f"Record with ID {record_id} not found.")
    except Exception as e:
        logging.error(f"Error deleting record {record_id}: {e}")
        raise
