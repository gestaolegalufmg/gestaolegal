"""Notificações internas (módulo "Notificações" da v2)."""

from datetime import date, datetime, timedelta
from io import BytesIO

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data


@pytest.fixture(autouse=True)
def _limpar(app):
    with app.app_context():
        clean_tables("notificacao")
    yield


def _me(client: FlaskClient, headers: dict[str, str]) -> int:
    return get_success_data(client.get("/api/user/me", headers=headers))["id"]


def _listar(client: FlaskClient, headers: dict[str, str]) -> dict:
    return get_success_data(client.get("/api/notificacao/", headers=headers))


def _nao_lidas(client: FlaskClient, headers: dict[str, str]) -> int:
    return get_success_data(client.get("/api/notificacao/nao-lidas", headers=headers))["total"]


def _criar_caso(client: FlaskClient, headers: dict[str, str], **campos) -> dict:
    payload = {"area_direito": "penal", "situacao_deferimento": "deferido", "ids_clientes": [], **campos}
    response = client.post("/api/caso/", json=payload, headers=headers)
    assert response.status_code == 201, response.get_json()
    return get_success_data(response)


class TestCaso:
    def test_cadastro_avisa_envolvidos_menos_o_executor(
        self, client, auth_headers, non_admin_auth_headers, estagiario_auth_headers
    ):
        admin_id = _me(client, auth_headers)
        orient_id = _me(client, non_admin_auth_headers)
        estag_id = _me(client, estagiario_auth_headers)

        caso = _criar_caso(
            client, auth_headers,
            id_usuario_responsavel=admin_id, id_orientador=orient_id, id_estagiario=estag_id,
        )

        assert _nao_lidas(client, auth_headers) == 0  # executor não se notifica
        lista = _listar(client, non_admin_auth_headers)
        assert lista["total"] == 1
        n = lista["items"][0]
        assert n["acao"] == f"Cadastrado no caso {caso['id']}"
        assert n["tipo"] == "caso" and n["id_caso"] == caso["id"]
        assert n["executor"] and n["lida"] is False
        assert _nao_lidas(client, estagiario_auth_headers) == 1

    def test_mesmo_usuario_em_dois_papeis_recebe_uma_vez(self, client, auth_headers, estagiario_auth_headers):
        estag_id = _me(client, estagiario_auth_headers)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id, id_estagiario=estag_id)
        assert _listar(client, estagiario_auth_headers)["total"] == 1

    def test_edicao_avisa_so_quem_entrou(self, client, auth_headers, non_admin_auth_headers, estagiario_auth_headers):
        admin_id = _me(client, auth_headers)
        orient_id = _me(client, non_admin_auth_headers)
        estag_id = _me(client, estagiario_auth_headers)
        caso = _criar_caso(client, auth_headers, id_usuario_responsavel=admin_id, id_orientador=orient_id)
        assert _listar(client, non_admin_auth_headers)["total"] == 1

        response = client.put(
            f"/api/caso/{caso['id']}", json={"id_estagiario": estag_id, "descricao": "x"}, headers=auth_headers
        )
        assert response.status_code == 200
        assert _listar(client, non_admin_auth_headers)["total"] == 1  # orientador já estava
        assert _listar(client, estagiario_auth_headers)["total"] == 1


class TestEventoLembrete:
    def test_evento_com_responsavel(self, client, auth_headers, estagiario_auth_headers):
        estag_id = _me(client, estagiario_auth_headers)
        caso = _criar_caso(client, auth_headers, id_usuario_responsavel=_me(client, auth_headers))
        response = client.post(
            f"/api/caso/{caso['id']}/eventos",
            data={"tipo": "reuniao", "data_evento": "2026-09-10", "descricao": "Reunião", "id_usuario_responsavel": str(estag_id)},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        assert response.status_code == 201, response.get_json()
        evento = get_success_data(response)
        n = _listar(client, estagiario_auth_headers)["items"][0]
        assert n["tipo"] == "evento"
        assert n["id_caso"] == caso["id"] and n["id_referencia"] == evento["id"]
        assert n["acao"] == f"Cadastrado no evento {evento['num_evento']} do caso {caso['id']}"
        assert n["detalhe"] == "Reunião"

    def test_evento_sem_responsavel_nao_notifica(self, client, auth_headers, estagiario_auth_headers):
        caso = _criar_caso(client, auth_headers, id_usuario_responsavel=_me(client, auth_headers))
        client.post(
            f"/api/caso/{caso['id']}/eventos",
            data={"tipo": "reuniao", "data_evento": "2026-09-10"},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        assert _listar(client, estagiario_auth_headers)["total"] == 0

    def test_lembrete(self, client, auth_headers, estagiario_auth_headers):
        estag_id = _me(client, estagiario_auth_headers)
        caso = _criar_caso(client, auth_headers, id_usuario_responsavel=_me(client, auth_headers))
        response = client.post(
            f"/api/caso/{caso['id']}/lembretes",
            json={"id_usuario": estag_id, "data_lembrete": "2026-09-15T00:00:00", "descricao": "Protocolar"},
            headers=auth_headers,
        )
        assert response.status_code == 201, response.get_json()
        lembrete = get_success_data(response)
        n = _listar(client, estagiario_auth_headers)["items"][0]
        assert n["tipo"] == "lembrete"
        assert n["id_referencia"] == lembrete["id"]
        assert n["acao"] == f"Cadastrado no lembrete {lembrete['num_lembrete']} do caso {caso['id']}"
        assert n["detalhe"] == "Protocolar"


class TestPlantao:
    def _configurar(self, client, headers, abertura: datetime):
        payload = {
            "dias": [(date.today() + timedelta(days=1)).isoformat()],
            "data_abertura": abertura.isoformat(timespec="seconds"),
            "data_fechamento": (abertura + timedelta(days=30)).isoformat(timespec="seconds"),
        }
        response = client.put("/api/plantao/configuracao", json=payload, headers=headers)
        assert response.status_code == 200, response.get_json()

    def test_abertura_e_aviso_geral_para_orient_e_estag(
        self, client, auth_headers, non_admin_auth_headers, estagiario_auth_headers, prof_auth_headers
    ):
        abertura = datetime.now().replace(microsecond=0) - timedelta(days=1)
        self._configurar(client, auth_headers, abertura)

        for headers in (non_admin_auth_headers, estagiario_auth_headers):
            lista = _listar(client, headers)
            assert lista["total"] == 1
            assert lista["items"][0]["acao"] == "Abertura do plantão"
            assert lista["items"][0]["tipo"] == "plantao"
            assert lista["items"][0]["id_usu_notificar"] is None
        assert _listar(client, prof_auth_headers)["total"] == 0
        assert _listar(client, auth_headers)["total"] == 0

        # Salvar de novo sem mudar a abertura não repete o aviso.
        self._configurar(client, auth_headers, abertura)
        assert _listar(client, estagiario_auth_headers)["total"] == 1

        # Mudar a abertura avisa de novo.
        self._configurar(client, auth_headers, abertura + timedelta(hours=1))
        assert _listar(client, estagiario_auth_headers)["total"] == 2


class TestLeitura:
    def test_marcar_lida_e_todas(self, client, auth_headers, estagiario_auth_headers, non_admin_auth_headers):
        estag_id = _me(client, estagiario_auth_headers)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        assert _nao_lidas(client, estagiario_auth_headers) == 2

        primeira = _listar(client, estagiario_auth_headers)["items"][0]["id"]
        assert client.patch(f"/api/notificacao/{primeira}/lida", headers=estagiario_auth_headers).status_code == 200
        assert _nao_lidas(client, estagiario_auth_headers) == 1
        assert _listar(client, estagiario_auth_headers)["items"][0]["lida"] is True

        # Outro usuário não marca notificação alheia.
        assert client.patch(f"/api/notificacao/{primeira}/lida", headers=non_admin_auth_headers).status_code == 404

        data = get_success_data(client.patch("/api/notificacao/lidas", headers=estagiario_auth_headers))
        assert data["total"] == 1
        assert _nao_lidas(client, estagiario_auth_headers) == 0

    def test_paginacao(self, client, auth_headers, estagiario_auth_headers):
        estag_id = _me(client, estagiario_auth_headers)
        for _ in range(3):
            _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        data = get_success_data(client.get("/api/notificacao/?per_page=2", headers=estagiario_auth_headers))
        assert len(data["items"]) == 2 and data["total"] == 3 and data["total_pages"] == 2

    def test_exige_login(self, client):
        assert client.get("/api/notificacao/").status_code == 401


class TestArquivamento:
    def _arquivar(self, client, headers, id: int, arquivar: bool = True):
        return client.patch(
            f"/api/notificacao/{id}/arquivada", json={"arquivar": arquivar}, headers=headers
        )

    def test_arquivada_sai_da_lista_padrao_e_do_contador(
        self, client, auth_headers, estagiario_auth_headers
    ):
        estag_id = _me(client, estagiario_auth_headers)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        alvo = _listar(client, estagiario_auth_headers)["items"][0]["id"]

        assert self._arquivar(client, estagiario_auth_headers, alvo).status_code == 200
        assert _nao_lidas(client, estagiario_auth_headers) == 1

        ativas = _listar(client, estagiario_auth_headers)
        assert ativas["total"] == 1 and alvo not in [n["id"] for n in ativas["items"]]

        arquivadas = get_success_data(
            client.get("/api/notificacao/?arquivadas=sim", headers=estagiario_auth_headers)
        )
        assert [n["id"] for n in arquivadas["items"]] == [alvo]
        assert arquivadas["items"][0]["data_arquivamento"] is not None

        todas = get_success_data(
            client.get("/api/notificacao/?arquivadas=todas", headers=estagiario_auth_headers)
        )
        assert todas["total"] == 2

    def test_desarquivar_devolve_para_a_lista(
        self, client, auth_headers, estagiario_auth_headers
    ):
        estag_id = _me(client, estagiario_auth_headers)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        alvo = _listar(client, estagiario_auth_headers)["items"][0]["id"]

        self._arquivar(client, estagiario_auth_headers, alvo)
        assert _listar(client, estagiario_auth_headers)["total"] == 0

        assert self._arquivar(client, estagiario_auth_headers, alvo, False).status_code == 200
        ativas = _listar(client, estagiario_auth_headers)
        assert ativas["total"] == 1 and ativas["items"][0]["data_arquivamento"] is None
        assert _nao_lidas(client, estagiario_auth_headers) == 1

    def test_arquivar_lidas_nao_toca_nas_nao_lidas(
        self, client, auth_headers, estagiario_auth_headers
    ):
        estag_id = _me(client, estagiario_auth_headers)
        for _ in range(3):
            _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        lida = _listar(client, estagiario_auth_headers)["items"][0]["id"]
        client.patch(f"/api/notificacao/{lida}/lida", headers=estagiario_auth_headers)

        data = get_success_data(
            client.patch("/api/notificacao/arquivadas", headers=estagiario_auth_headers)
        )
        assert data["total"] == 1
        assert _listar(client, estagiario_auth_headers)["total"] == 2
        assert _nao_lidas(client, estagiario_auth_headers) == 2

    def test_nao_arquiva_notificacao_alheia(
        self, client, auth_headers, estagiario_auth_headers, non_admin_auth_headers
    ):
        estag_id = _me(client, estagiario_auth_headers)
        _criar_caso(client, auth_headers, id_usuario_responsavel=estag_id)
        alvo = _listar(client, estagiario_auth_headers)["items"][0]["id"]
        assert self._arquivar(client, non_admin_auth_headers, alvo).status_code == 404

    def test_filtro_invalido(self, client, estagiario_auth_headers):
        response = client.get("/api/notificacao/?arquivadas=xpto", headers=estagiario_auth_headers)
        assert response.status_code == 400
