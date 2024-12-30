from sqlalchemy import create_engine
from db.object import Base, Object, ObjectRecord
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.db_fs import delete_file
from sqlalchemy.orm import joinedload
import paths
from paths import Paths


engine = create_engine(f"sqlite:///{paths.DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def insert_object(object: Object):
    with get_session() as session:
        session.add(object)
        session.flush()
        return object.id


def insert_record(object_id: int, object_record: ObjectRecord):
    with get_session() as session:
        object = (
            session.query(Object).options(joinedload(Object.records)).get(object_id)
        )
        object_record.parent = object
        object.records.append(object_record)
        session.add(object_record)
        session.flush()
        return object_record.id


def get_all_objects_for_list():
    with get_session() as session:
        return session.query(Object.id, Object.name, Object.date_created).all()


def get_all_records_for_list(object_id):
    with get_session() as session:
        return (
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


def get_object_by_id(object_id):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        if obj:
            return {
                "id": obj.id,
                "name": obj.name,
                "date_created": obj.date_created,
                "frame_path": obj.frame_path,
                "in_frame": obj.in_frame,
                "out_frame": obj.out_frame,
            }
        return None


def get_record_by_id(record_id):
    with get_session() as session:
        record = session.query(ObjectRecord).filter_by(id=record_id).first()
        if record:
            return {
                "id": record.id,
                "object_id": record.object_id,
                "file_path": record.file_path,
                "date_uploaded": record.date_uploaded,
                "is_processed": record.is_processed,
            }


def get_object_name_by_id(object_id):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        if obj:
            return obj.name
        return None


def update_object_by_id(object_id, name, in_frame, out_frame):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        if obj:
            obj.name = name
            obj.in_frame = in_frame
            obj.out_frame = out_frame


def delete_object_by_id(object_id):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        for record in obj.records:
            delete_file(Paths.record_data_npz(record.id))
        if obj:
            delete_file(obj.frame_path)
            session.delete(obj)


def update_record_status(record_id):
    with get_session() as session:
        record = session.query(ObjectRecord).filter_by(id=record_id).first()
        if record:
            record.is_processed = True


def delete_record_by_id(record_id):
    with get_session() as session:
        record = session.query(ObjectRecord).filter_by(id=record_id).first()
        delete_file(Paths.record_data_npz(record.id))
        if record:
            session.delete(record)
