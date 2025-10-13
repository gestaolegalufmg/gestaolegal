import logging
from functools import wraps
from typing import Callable, Literal, ParamSpec

from flask import make_response, request
from flask.typing import ResponseReturnValue

from gestaolegal.models.user import UserInfo
from gestaolegal.utils.jwt_auth import JWTAuth
from gestaolegal.utils.request_context import RequestContext

logger = logging.getLogger(__name__)

UserRole = Literal["admin", "colab_proj", "orient", "estag_direito", "colab_ext"]
P = ParamSpec("P")


def authenticated(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return make_response("Authorization token is missing", 401)

        try:
            token = auth_header.split(" ", maxsplit=1)[1]
        except IndexError:
            return make_response("Invalid authorization header format", 401)

        user: UserInfo | None = JWTAuth.get_user_from_token(token)

        if not user:
            return make_response("Invalid or expired token", 401)

        RequestContext.set_current_user(user)

        return func(*args, **kwargs)

    return wrapper


def authorized(
    *roles: UserRole,
) -> Callable[[Callable[P, ResponseReturnValue]], Callable[P, ResponseReturnValue]]:
    def decorator(
        func: Callable[P, ResponseReturnValue],
    ) -> Callable[P, ResponseReturnValue]:
        @authenticated
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ResponseReturnValue:
            user = RequestContext.get_current_user()

            if user.urole not in roles:
                return make_response("Forbidden", 403)

            return func(*args, **kwargs)

        return wrapper

    return decorator
