from functools import wraps
import inspect
from flask import make_response, request, Response
from gestaolegal.utils.jwt_auth import JWTAuth
from typing import Callable, TypeVar, ParamSpec, Concatenate, overload, cast
from gestaolegal.models.user import User
import logging

logger = logging.getLogger(__name__)

P = ParamSpec('P')
R = TypeVar('R')

@overload
def api_auth_required(
    f: Callable[Concatenate[User, P], R]
) -> Callable[P, R | Response]: ...

@overload
def api_auth_required(
    f: Callable[P, R]
) -> Callable[P, R | Response]: ...

def api_auth_required(
    f: Callable[..., R]
) -> Callable[..., R | Response]:
    @wraps(f)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R | Response:
        token: str | None = None
        auth_header: str | None = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return make_response("Invalid authorization header format", 401)
        
        if not token:
            return make_response("Authorization token is missing", 401)
        
        user: User | None = JWTAuth.get_user_from_token(token)
        
        if not user:
            return make_response("Invalid or expired token", 401)
        
        sig = inspect.signature(f)
        if 'current_user' in sig.parameters:
            return f(*args, current_user=user, **kwargs)
        else:
            return f(*args, **kwargs)
    
    return decorated_function