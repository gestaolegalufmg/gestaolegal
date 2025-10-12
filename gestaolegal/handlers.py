from flask import Flask

from gestaolegal.database.session import close_session


def register_handlers(app: Flask):
    @app.teardown_appcontext
    def teardown_db(exception: Exception | None):  # pyright: ignore[reportUnusedFunction]
        close_session(exception)

    return app
