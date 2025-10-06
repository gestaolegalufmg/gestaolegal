from flask import Flask

from gestaolegal.database.session import get_session


def register_handlers(app: Flask):
    @app.before_request
    def before_request():  # pyright: ignore[reportUnusedFunction]
        return None

    @app.teardown_appcontext
    def teardown_appcontext(exception: Exception | None):  # pyright: ignore[reportUnusedFunction]
        session = get_session()
        if exception:
            session.rollback()
        else:
            if session:
                session.commit()

        if session:
            session.close()

    return app
