from dataclasses import fields

import pytest

from gestaolegal.models.user import UserInfo
from gestaolegal.utils.request_context import RequestContext


def _user_info() -> UserInfo:
    # UserInfo tem muitos campos obrigatorios e nenhum deles importa aqui:
    # o contexto so guarda e devolve a instancia.
    return UserInfo(**{campo.name: None for campo in fields(UserInfo)})


@pytest.fixture(autouse=True)
def limpar_contexto():
    RequestContext.clear()
    yield
    RequestContext.clear()


def test_unidade_ativa_ausente_levanta_runtime_error():
    with pytest.raises(RuntimeError):
        RequestContext.get_unidade_ativa()


def test_set_e_get_unidade_ativa():
    RequestContext.set_unidade_ativa(2)
    assert RequestContext.get_unidade_ativa() == 2


def test_clear_zera_usuario_e_unidade():
    RequestContext.set_current_user(_user_info())
    RequestContext.set_unidade_ativa(1)

    RequestContext.clear()

    with pytest.raises(RuntimeError):
        RequestContext.get_current_user()
    with pytest.raises(RuntimeError):
        RequestContext.get_unidade_ativa()
