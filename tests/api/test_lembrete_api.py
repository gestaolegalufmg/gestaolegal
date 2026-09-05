from typing import Any

from flask.testing import FlaskClient

from tests.api.conftest import get_success_data


def _criar_caso(
    client: FlaskClient, headers: dict[str, str], caso_data: dict[str, Any]
) -> int:
    response = client.post("/api/caso/", json=caso_data, headers=headers)
    assert response.status_code == 201
    return get_success_data(response)["id"]


def _criar_lembrete(
    client: FlaskClient,
    headers: dict[str, str],
    caso_id: int,
    descricao: str = "Protocolar peça",
) -> dict[str, Any]:
    response = client.post(
        f"/api/caso/{caso_id}/lembretes",
        json={
            "id_usuario": 1,
            "data_lembrete": "2026-09-15T00:00:00",
            "descricao": descricao,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.get_json()
    return get_success_data(response)


def test_criar_e_listar_lembrete(
    client: FlaskClient,
    auth_headers: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_id = _criar_caso(client, auth_headers, sample_caso_data)
    lembrete = _criar_lembrete(client, auth_headers, caso_id)

    assert lembrete["num_lembrete"] == 1
    assert lembrete["descricao"] == "Protocolar peça"

    listagem = get_success_data(
        client.get(f"/api/caso/{caso_id}/lembretes", headers=auth_headers)
    )
    assert [item["id"] for item in listagem] == [lembrete["id"]]


def test_lembrete_herda_a_unidade_do_caso(
    client: FlaskClient,
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """O lembrete nasce na unidade do caso, não na unidade padrão."""
    caso_id = _criar_caso(client, auth_headers_nl, sample_caso_data)
    lembrete = _criar_lembrete(client, auth_headers_nl, caso_id)

    assert lembrete["unidade_id"] == 2


def test_lembretes_de_caso_de_outra_unidade_nao_aparecem(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    """Lembrete de caso da unidade 2 não é listado pela unidade 1."""
    caso_nl = _criar_caso(client, auth_headers_nl, sample_caso_data)
    _criar_lembrete(client, auth_headers_nl, caso_nl)

    assert (
        client.get(
            f"/api/caso/{caso_nl}/lembretes", headers=auth_headers_nl
        ).status_code
        == 200
    )
    assert (
        client.get(f"/api/caso/{caso_nl}/lembretes", headers=auth_headers).status_code
        == 404
    )


def test_lembrete_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_nl = _criar_caso(client, auth_headers_nl, sample_caso_data)
    lembrete_id = _criar_lembrete(client, auth_headers_nl, caso_nl)["id"]

    rota = f"/api/caso/{caso_nl}/lembretes/{lembrete_id}"
    assert client.get(rota, headers=auth_headers).status_code == 404
    assert (
        client.put(
            rota, json={"descricao": "Tentativa"}, headers=auth_headers
        ).status_code
        == 404
    )
    assert client.delete(rota, headers=auth_headers).status_code == 404


def test_criar_lembrete_em_caso_de_outra_unidade_responde_404(
    client: FlaskClient,
    auth_headers: dict[str, str],
    auth_headers_nl: dict[str, str],
    sample_caso_data: dict[str, Any],
) -> None:
    caso_nl = _criar_caso(client, auth_headers_nl, sample_caso_data)

    response = client.post(
        f"/api/caso/{caso_nl}/lembretes",
        json={
            "id_usuario": 1,
            "data_lembrete": "2026-09-15T00:00:00",
            "descricao": "Tentativa de outra unidade",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
