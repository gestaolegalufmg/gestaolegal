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
    return create_engine(database_uri, **engine_options)


def get_db():
    if "db" not in g:
        engine = get_engine()

        Session = sessionmaker(bind=engine)
        g.db = Database()
        g.db.session = Session()

    def paginate(
        query: Query, page: int = 1, per_page: int = 20, error_out: bool = True
    ):
        if page < 1:
            if error_out:
                raise ValueError("Page number must be positive")
            page = 1

        if per_page < 1:
            if error_out:
                raise ValueError("Per page must be positive")
            per_page = 20

        total = query.count()

        pages = max(1, (total + per_page - 1) // per_page)

        if page > pages:
            if error_out:
                raise ValueError(f"Page {page} is out of range (max {pages})")
            page = pages

        items = query.limit(per_page).offset((page - 1) * per_page).all()

        class Pagination:
            def __init__(self, items, page, per_page, total, pages):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = pages

            def __iter__(self):
                return iter(self.items)

            def __len__(self):
                return len(self.items)

            @property
            def has_next(self):
                return self.page < self.pages

            @property
            def has_prev(self):
                return self.page > 1

            @property
            def next_num(self):
                return self.page + 1 if self.has_next else None

            @property
            def prev_num(self):
                return self.page - 1 if self.has_prev else None

            @property
            def first_item(self):
                return ((self.page - 1) * self.per_page) + 1 if self.total else 0

            @property
            def last_item(self):
                return min(self.page * self.per_page, self.total)

            def iter_pages(
                self, left_edge=2, right_edge=2, left_current=2, right_current=2
            ):
                last = self.pages

                for num in range(1, min(left_edge + 1, last + 1)):
                    yield num

                if left_edge + 1 < self.page - left_current:
                    yield None

                start = max(left_edge + 1, self.page - left_current)
                end = min(last + 1, self.page + right_current + 1)

                for num in range(start, end):
                    yield num

                if self.page + right_current < last - right_edge:
                    yield None

                start = max(self.page + right_current + 1, last - right_edge + 1)
                for num in range(start, last + 1):
                    yield num

        return Pagination(items, page, per_page, total, pages)

    g.db.paginate = paginate

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.session.close()


def init_app(app):
    app.teardown_appcontext(close_db)
