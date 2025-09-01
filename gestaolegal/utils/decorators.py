from functools import wraps

from flask import current_app, flash, redirect, url_for
from flask_login import current_user


def login_required(role=["ANY"]):
    """
    Decorator to require login and optionally specific roles.

    Args:
        role (list): List of allowed roles. Defaults to ["ANY"] which allows all authenticated users.

    Returns:
        Decorated function
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()

            urole = current_user.urole
            if (urole not in role) and (role != ["ANY"]):
                flash("Você não tem permissão para acessar essa página!", "warning")
                return redirect(url_for("principal.index"))

            return fn(*args, **kwargs)

        return decorated_view

    return wrapper
