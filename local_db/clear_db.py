from sqlalchemy import create_engine
from object import Base, Object, ObjectRecord
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


def delete_all_instances():
    with get_session() as session:
        session.query(Object).delete()
        session.query(ObjectRecord).delete()
        session.commit()


delete_all_instances()
