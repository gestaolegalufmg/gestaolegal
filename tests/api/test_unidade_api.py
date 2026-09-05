"""Endpoints /api/unidades (F4.1).

As unidades criadas aqui não são limpas entre testes (o `clean_db` só varre
usuários), então cada caso usa nome e sigla próprios.
"""

from flask.testing import FlaskClient

from tests.api.conftest import UNIDADE_BH, UNIDADE_NL, get_success_data


def _sem_unidade(headers: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in headers.items() if k != "X-Unidade-Id"}


def test_listar_dispensa_o_header_de_unidade(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.get("/api/unidades/", headers=_sem_unidade(auth_headers))

    assert response.status_code == 200
    ids = [u["id"] for u in get_success_data(response)]
    assert UNIDADE_BH in ids
    assert UNIDADE_NL in ids


def test_listar_exige_autenticacao(client: FlaskClient, unidades: None):
    assert client.get("/api/unidades/").status_code == 401


def test_listar_traz_so_as_ativas(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    criada = get_success_data(
        client.post(
            "/api/unidades/",
            headers=auth_headers,
            json={"nome": "Unidade Inativa", "sigla": "INA", "ativa": False},
        )
    )

    siglas = [u["sigla"] for u in get_success_data(
        client.get("/api/unidades/", headers=auth_headers)
    )]

    assert "INA" not in siglas

    response = client.put(
        f"/api/unidades/{criada['id']}", headers=auth_headers, json={"ativa": True}
    )
    assert response.status_code == 200

    siglas = [u["sigla"] for u in get_success_data(
        client.get("/api/unidades/", headers=auth_headers)
    )]
    assert "INA" in siglas


def test_criar_como_admin(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.post(
        "/api/unidades/",
        headers=auth_headers,
        json={"nome": "Contagem", "sigla": "ctg"},
    )

    assert response.status_code == 201
    data = get_success_data(response)
    assert data["nome"] == "Contagem"
    assert data["sigla"] == "CTG"
    assert data["ativa"] is True


def test_criar_com_nome_repetido_responde_400(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.post(
        "/api/unidades/",
        headers=auth_headers,
        json={"nome": "Belo Horizonte", "sigla": "BHX"},
    )

    assert response.status_code == 400


def test_criar_como_nao_admin_responde_403(
    client: FlaskClient, non_admin_auth_headers: dict[str, str], unidades: None
):
    response = client.post(
        "/api/unidades/",
        headers=non_admin_auth_headers,
        json={"nome": "Betim", "sigla": "BTM"},
    )

    assert response.status_code == 403


def test_atualizar_como_admin(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    criada = get_success_data(
        client.post(
            "/api/unidades/",
            headers=auth_headers,
            json={"nome": "Sabará", "sigla": "SBR"},
        )
    )

    response = client.put(
        f"/api/unidades/{criada['id']}",
        headers=auth_headers,
        json={"nome": "Sabará Centro"},
    )

    assert response.status_code == 200
    data = get_success_data(response)
    assert data["nome"] == "Sabará Centro"
    assert data["sigla"] == "SBR"


def test_atualizar_inexistente_responde_404(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    response = client.put(
        "/api/unidades/999999", headers=auth_headers, json={"nome": "Fantasma"}
    )

    assert response.status_code == 404


def test_atualizar_como_nao_admin_responde_403(
    client: FlaskClient, non_admin_auth_headers: dict[str, str], unidades: None
):
    response = client.put(
        f"/api/unidades/{UNIDADE_BH}",
        headers=non_admin_auth_headers,
        json={"nome": "Nova BH"},
    )

    assert response.status_code == 403


def test_listar_com_incluir_inativas_traz_as_inativas_para_admin(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    client.post(
        "/api/unidades/",
        headers=auth_headers,
        json={"nome": "Unidade Desativada Admin", "sigla": "UDA", "ativa": False},
    )

    siglas = [
        u["sigla"]
        for u in get_success_data(
            client.get("/api/unidades/?incluir_inativas=1", headers=auth_headers)
        )
    ]

    assert "UDA" in siglas
    assert {"BH", "NL"} <= set(siglas)


def test_listar_com_incluir_inativas_de_nao_admin_traz_so_ativas(
    client: FlaskClient,
    auth_headers: dict[str, str],
    non_admin_auth_headers: dict[str, str],
    unidades: None,
):
    client.post(
        "/api/unidades/",
        headers=auth_headers,
        json={"nome": "Unidade Desativada Comum", "sigla": "UDC", "ativa": False},
    )

    response = client.get(
        "/api/unidades/?incluir_inativas=1", headers=non_admin_auth_headers
    )

    assert response.status_code == 200
    siglas = [u["sigla"] for u in get_success_data(response)]
    assert "UDC" not in siglas
    assert {"BH", "NL"} <= set(siglas)


def test_reativar_por_put_devolve_a_unidade_ao_seletor(
    client: FlaskClient, auth_headers: dict[str, str], unidades: None
):
    criada = get_success_data(
        client.post(
            "/api/unidades/",
            headers=auth_headers,
            json={"nome": "Unidade Reativada", "sigla": "URE", "ativa": False},
        )
    )

    def siglas_do_seletor() -> list[str]:
        return [
            u["sigla"]
            for u in get_success_data(
                client.get("/api/unidades/", headers=auth_headers)
            )
        ]

    assert "URE" not in siglas_do_seletor()

    assert (
        client.put(
            f"/api/unidades/{criada['id']}", headers=auth_headers, json={"ativa": True}
        ).status_code
        == 200
    )

    assert "URE" in siglas_do_seletor()
