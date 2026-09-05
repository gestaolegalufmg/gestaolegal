from contextvars import ContextVar

from gestaolegal.models.user import UserInfo

_current_user: ContextVar[UserInfo | None] = ContextVar("current_user", default=None)
_unidade_ativa: ContextVar[int | None] = ContextVar("unidade_ativa", default=None)


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
    def set_unidade_ativa(unidade_id: int) -> None:
        _unidade_ativa.set(unidade_id)

    @staticmethod
    def get_unidade_ativa() -> int:
        unidade_id = _unidade_ativa.get()
        if unidade_id is None:
            raise RuntimeError("No active unidade in current request context")
        return unidade_id

    @staticmethod
    def clear() -> None:
        _current_user.set(None)
        _unidade_ativa.set(None)
