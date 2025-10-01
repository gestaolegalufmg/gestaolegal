import os

from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import Query, Session, sessionmaker


class Database:
    session: Session


def get_database_uri():
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    if not all([db_user, db_password, db_host, db_name]):
        raise ValueError("Database configuration is incomplete")

    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"


def get_engine():
    database_uri = get_database_uri()
    engine_options = os.environ.get("SQLALCHEMY_ENGINE_OPTIONS", {})
    engine_options["echo"] = True
    return create_engine(database_uri, **engine_options)


def get_db():
    if "db" not in g:
        engine = get_engine()

        Session = sessionmaker(bind=engine)
        g.db = Database()
        g.db.session = Session()

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.session.close()


def init_app(app):
    app.teardown_appcontext(close_db)
