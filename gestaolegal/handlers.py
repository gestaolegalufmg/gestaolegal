from flask import Flask

from gestaolegal.database.session import cleanup_session, get_session


def register_handlers(app: Flask):
    @app.before_request
    def before_request():  # pyright: ignore[reportUnusedFunction]
        return None

    @app.teardown_appcontext
    def teardown_appcontext(exception: Exception | None):  # pyright: ignore[reportUnusedFunction]
        session = get_session()
        if session:
            try:
                if exception:
                    session.rollback()
                else:
                    session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
                cleanup_session()

    return app
