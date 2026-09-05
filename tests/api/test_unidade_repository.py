from datetime import datetime

import pytest
from flask import Flask

from gestaolegal.models.unidade import Unidade
from gestaolegal.repositories.unidade_repository import UnidadeRepository

from .conftest import UNIDADE_BH, UNIDADE_NL

# Usuários fictícios: os vínculos só exercitam usuarios_unidades, e o SQLite dos
# testes não impõe as chaves estrangeiras.
USUARIO_A = 90001
USUARIO_B = 90002


@pytest.fixture
def repo(app: Flask, unidades: None):
    with app.app_context():
        repository = UnidadeRepository()
        yield repository
        repository.session.rollback()
        repository.session.close()


def test_find_by_id_devolve_unidade(repo: UnidadeRepository) -> None:
    unidade = repo.find_by_id(UNIDADE_BH)

    assert unidade is not None
    assert isinstance(unidade, Unidade)
    assert unidade.nome == "Belo Horizonte"
    assert unidade.sigla == "BH"
    assert unidade.ativa is True


def test_find_by_id_inexistente_devolve_none(repo: UnidadeRepository) -> None:
    assert repo.find_by_id(999999) is None


def test_create_e_list_ativas_ignora_inativa(repo: UnidadeRepository) -> None:
    novo_id = repo.create(
        {
            "nome": "Unidade Teste Inativa",
            "sigla": "UTI",
            "ativa": False,
            "criado": datetime.now(),
        }
    )

    siglas = [u.sigla for u in repo.list_ativas()]

    assert "UTI" not in siglas
    assert {"BH", "NL"} <= set(siglas)

    repo.update(novo_id, {"ativa": True})
    assert "UTI" in [u.sigla for u in repo.list_ativas()]


def test_vincular_substitui_vinculos(repo: UnidadeRepository) -> None:
    repo.vincular(USUARIO_A, [UNIDADE_BH, UNIDADE_NL])
    assert [u.id for u in repo.unidades_do_usuario(USUARIO_A)] == [
        UNIDADE_BH,
        UNIDADE_NL,
    ]

    repo.vincular(USUARIO_A, [UNIDADE_NL])
    assert [u.id for u in repo.unidades_do_usuario(USUARIO_A)] == [UNIDADE_NL]


def test_unidades_do_usuario_sem_vinculo(repo: UnidadeRepository) -> None:
    assert repo.unidades_do_usuario(USUARIO_B) == []


def test_usuario_pertence(repo: UnidadeRepository) -> None:
    repo.vincular(USUARIO_B, [UNIDADE_BH])

    assert repo.usuario_pertence(USUARIO_B, UNIDADE_BH) is True
    assert repo.usuario_pertence(USUARIO_B, UNIDADE_NL) is False
