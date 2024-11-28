from sqlalchemy import create_engine
from local_db.object import Base, Object, ObjectRecord
from sqlalchemy.orm import sessionmaker, joinedload
from contextlib import contextmanager


engine = create_engine("sqlite:///objects.db", echo=False)
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


def insert_object_and_record(object: Object, object_record: ObjectRecord):
    with get_session() as session:
        object.records.append(object_record)
        object_record.parent = object
        session.add(object)
        session.add(object_record)


def insert_record(object_id: int, object_record: ObjectRecord):
    with get_session() as session:
        object = session.query(Object).filter_by(id=object_id).first()
        object_record.parent = object
        object.records.append(object_record)
        session.add(object_record)


def get_all_object_ids_and_names():
    with get_session() as session:
        return session.query(Object.id, Object.name).all()


def get_all_object_records_datetimes(object_id):
    with get_session() as session:
        records = (
            session.query(ObjectRecord.date_uploaded)
            .join(ObjectRecord.parent)
            .filter(Object.id == object_id)
            .all()
        )
        return [record.date_uploaded for record in records]


### get functions here return only dict, not object itself
def get_object_by_id(object_id):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        if obj:
            return {
                "name": obj.name,
                "frame_path": obj.frame_path,
                "in_frame": obj.in_frame,
                "out_frame": obj.out_frame,
            }
        return None


def get_object_name_by_id(object_id):
    with get_session() as session:
        obj = session.query(Object).filter_by(id=object_id).first()
        if obj:
            return obj.name
        return None
