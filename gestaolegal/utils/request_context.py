from contextvars import ContextVar

from gestaolegal.models.user import UserInfo

_current_user: ContextVar[UserInfo | None] = ContextVar("current_user", default=None)


class RequestContext:
    @staticmethod
    def set_current_user(user: UserInfo) -> None:
        _current_user.set(user)

    @staticmethod
    def get_current_user() -> UserInfo:
        user = _current_user.get()
        if user is None:
            raise RuntimeError("No authenticated user in current request context")
        return user

    @staticmethod
    def clear() -> None:
        _current_user.set(None)
