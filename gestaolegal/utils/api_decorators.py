import logging
from functools import wraps
from typing import Callable, Literal, ParamSpec, overload

from flask import make_response, request
from flask.typing import ResponseReturnValue

from gestaolegal.models.user import UserInfo
from gestaolegal.exceptions import ForbiddenException, ValidationException
from gestaolegal.utils.jwt_auth import JWTAuth
from gestaolegal.utils.request_context import RequestContext

logger = logging.getLogger(__name__)

UserRole = Literal[
    "admin", "colab_proj", "orient", "estag_direito", "colab_ext", "prof"
]
P = ParamSpec("P")

UNIDADE_HEADER = "X-Unidade-Id"


def _resolver_unidade_ativa(user: UserInfo) -> None:
    """Lê o X-Unidade-Id da requisição e o guarda no RequestContext.

    Levanta ValidationException (400) quando o header falta ou não é número, e
    ForbiddenException (403) quando o usuário não está vinculado à unidade.
    """
    header = request.headers.get(UNIDADE_HEADER)

    if not header:
        raise ValidationException("Unidade ativa não informada", field=UNIDADE_HEADER)

    try:
        unidade_id = int(header)
    except ValueError:
        raise ValidationException("Unidade ativa não informada", field=UNIDADE_HEADER)

    if unidade_id not in {unidade.id for unidade in user.unidades}:
        raise ForbiddenException("Você não tem acesso à unidade informada")

    RequestContext.set_unidade_ativa(unidade_id)


@overload
def authenticated(
    func: Callable[P, ResponseReturnValue],
) -> Callable[P, ResponseReturnValue]: ...


@overload
def authenticated(
    *, unidade: bool
) -> Callable[[Callable[P, ResponseReturnValue]], Callable[P, ResponseReturnValue]]: ...


def authenticated(
    func: Callable[P, ResponseReturnValue] | None = None, *, unidade: bool = True
):
    """Exige token válido e, por padrão, o header X-Unidade-Id.

    Aceita os dois usos: `@authenticated` (exige unidade) e
    `@authenticated(unidade=False)`, para as rotas que existem antes de haver
    unidade ativa — `GET /user/me`, `/user/opcoes` e a listagem de unidades do
    seletor.
    """

    def decorator(
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

            if unidade:
                _resolver_unidade_ativa(user)

            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


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
                raise ForbiddenException()

            return func(*args, **kwargs)

        return wrapper

    return decorator
