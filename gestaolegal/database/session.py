from flask import g, has_request_context
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gestaolegal.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, **Config.SQLALCHEMY_ENGINE_OPTIONS, echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    if not has_request_context():
        return SessionLocal()

    if "db_session" not in g:
        g.db_session = SessionLocal()

    return g.db_session


def close_session(error=None) -> None:
    session = g.pop("db_session", None)

    if session is not None:
        try:
            if error:
                session.rollback()
            else:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
