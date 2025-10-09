from contextvars import ContextVar

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gestaolegal.config import Config

CurrentSession: ContextVar[Session | None] = ContextVar("session", default=None)

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, **Config.SQLALCHEMY_ENGINE_OPTIONS, echo=False
)


def create_session():
    return sessionmaker(autocommit=False, autoflush=True, bind=engine)()


def get_session():
    session = CurrentSession.get()
    if session is None:
        session = create_session()
        CurrentSession.set(session)
    return session


def cleanup_session():
    CurrentSession.set(None)
