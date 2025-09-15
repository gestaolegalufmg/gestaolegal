from flask import current_app, g
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Query, Session, sessionmaker


class Database:
    session: Session


def get_db():
    if "db" not in g:
        config = current_app.config

        db_user = config.get("DB_USER")
        db_password = config.get("DB_PASSWORD")
        db_host = config.get("DB_HOST")
        db_name = config.get("DB_NAME")

        if not all([db_user, db_password, db_host, db_name]):
            raise ValueError("Database configuration is incomplete")

        database_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

        engine_options = config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        engine = create_engine(database_uri, **engine_options)

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
