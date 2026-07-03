from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data


def _criar_atendido(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
    nome: str,
    cpf: str,
) -> int:
    payload = {**sample_atendido_data, "nome": nome, "cpf": cpf}
    response = client.post("/api/atendido/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.json
    return get_success_data(response)["id"]


def _reset(client: FlaskClient) -> None:
    # Cada teste começa com a fila e os atendidos limpos.
    clean_tables("fila_atendimentos", "assistidos", "atendidos")


def test_preview_senha_por_grupo(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _reset(client)

    # Sem ninguém na fila, cada grupo começa em 01.
    for prioridade, esperado in [(0, "N01"), (1, "P01"), (2, "S01")]:
        response = client.get(
            f"/api/fila_atendimento/preview?prioridade={prioridade}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert get_success_data(response)["senha"] == esperado


def test_preview_prioridade_invalida(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    _reset(client)
    response = client.get(
        "/api/fila_atendimento/preview?prioridade=9", headers=auth_headers
    )
    assert response.status_code == 400


def test_incluir_gera_senha_consecutiva_e_independente(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _reset(client)
    a1 = _criar_atendido(client, auth_headers, sample_atendido_data, "Ana", "111")
    a2 = _criar_atendido(client, auth_headers, sample_atendido_data, "Bia", "222")
    a3 = _criar_atendido(client, auth_headers, sample_atendido_data, "Caio", "333")

    r1 = client.post(
        "/api/fila_atendimento/",
        json={"id_atendido": a1, "prioridade": 0, "psicologia": False},
        headers=auth_headers,
    )
    r2 = client.post(
        "/api/fila_atendimento/",
        json={"id_atendido": a2, "prioridade": 0, "psicologia": True},
        headers=auth_headers,
    )
    r3 = client.post(
        "/api/fila_atendimento/",
        json={"id_atendido": a3, "prioridade": 2, "psicologia": False},
        headers=auth_headers,
    )

    assert r1.status_code == 201
    assert get_success_data(r1)["senha"] == "N01"
    assert get_success_data(r2)["senha"] == "N02"
    # Grupo independente: super prioridade começa do 01 mesmo com normais na fila.
    assert get_success_data(r3)["senha"] == "S01"
    assert get_success_data(r2)["psicologia"] == 1


def test_fila_ordenada_por_prioridade_e_chegada(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _reset(client)
    normal = _criar_atendido(client, auth_headers, sample_atendido_data, "Normal", "1")
    prio = _criar_atendido(client, auth_headers, sample_atendido_data, "Prio", "2")
    super1 = _criar_atendido(client, auth_headers, sample_atendido_data, "Super1", "3")
    super2 = _criar_atendido(client, auth_headers, sample_atendido_data, "Super2", "4")

    # Inclui em ordem "embaralhada" de prioridade.
    for aid, prioridade in [(normal, 0), (super1, 2), (prio, 1), (super2, 2)]:
        resp = client.post(
            "/api/fila_atendimento/",
            json={"id_atendido": aid, "prioridade": prioridade},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    data = get_success_data(client.get("/api/fila_atendimento/", headers=auth_headers))
    nomes = [i["nome"] for i in data["fila"]]

    # super prioridade > prioridade > normal; entre supers, quem entrou antes primeiro.
    assert nomes == ["Super1", "Super2", "Prio", "Normal"]
    assert data["atendidos_cancelados"] == []


def test_chamar_e_cancelar_movem_para_concluidos(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _reset(client)
    a1 = _criar_atendido(client, auth_headers, sample_atendido_data, "Chamado", "1")
    a2 = _criar_atendido(client, auth_headers, sample_atendido_data, "Cancelado", "2")

    f1 = get_success_data(
        client.post(
            "/api/fila_atendimento/",
            json={"id_atendido": a1, "prioridade": 0},
            headers=auth_headers,
        )
    )
    f2 = get_success_data(
        client.post(
            "/api/fila_atendimento/",
            json={"id_atendido": a2, "prioridade": 0},
            headers=auth_headers,
        )
    )

    assert (
        client.post(
            f"/api/fila_atendimento/{f1['id']}/chamar", headers=auth_headers
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/fila_atendimento/{f2['id']}/cancelar", headers=auth_headers
        ).status_code
        == 200
    )

    data = get_success_data(client.get("/api/fila_atendimento/", headers=auth_headers))
    assert data["fila"] == []
    concluidos = {i["nome"]: i for i in data["atendidos_cancelados"]}
    assert concluidos["Chamado"]["status"] == 1
    assert concluidos["Cancelado"]["status"] == 2
    assert concluidos["Chamado"]["data_saida"] is not None
    # Concluídos em ordem cronológica de saída: chamado (antes) vem antes do
    # cancelado (depois).
    nomes_concluidos = [i["nome"] for i in data["atendidos_cancelados"]]
    assert nomes_concluidos == ["Chamado", "Cancelado"]


def test_nao_pode_chamar_quem_ja_saiu(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_atendido_data: dict[str, Any],
) -> None:
    _reset(client)
    a1 = _criar_atendido(client, auth_headers, sample_atendido_data, "Um", "1")
    f1 = get_success_data(
        client.post(
            "/api/fila_atendimento/",
            json={"id_atendido": a1, "prioridade": 0},
            headers=auth_headers,
        )
    )
    client.post(f"/api/fila_atendimento/{f1['id']}/chamar", headers=auth_headers)
    # Chamar de novo deve falhar (já saiu da fila).
    segunda = client.post(
        f"/api/fila_atendimento/{f1['id']}/chamar", headers=auth_headers
    )
    assert segunda.status_code == 400


def test_chamar_inexistente_404(
    client: FlaskClient, auth_headers: dict[str, str]
) -> None:
    _reset(client)
    response = client.post("/api/fila_atendimento/99999/chamar", headers=auth_headers)
    assert response.status_code == 404


def test_fila_requer_autenticacao(client: FlaskClient) -> None:
    assert client.get("/api/fila_atendimento/").status_code == 401
    assert client.post("/api/fila_atendimento/").status_code == 401
