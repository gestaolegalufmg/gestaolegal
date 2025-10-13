from flask import Flask

from gestaolegal.database.session import close_session
from gestaolegal.utils.request_context import RequestContext


def register_handlers(app: Flask):
    @app.teardown_appcontext
    def teardown_db(exception: BaseException | None):  # pyright: ignore[reportUnusedFunction]
        close_session(exception)
        RequestContext.clear()

    return app
