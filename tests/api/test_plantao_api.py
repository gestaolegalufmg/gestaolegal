from datetime import date, datetime, timedelta

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import (
    clean_tables,
    criar_usuario,
    get_success_data,
    headers_para,
)

TABELAS = ("dias_marcados_plantao", "dias_plantao", "plantao")


@pytest.fixture(autouse=True)
def _reset(app):
    with app.app_context():
        clean_tables(*TABELAS)
    yield


def _janela(dias_ate_fechar: int = 30) -> dict[str, str]:
    abertura = datetime.now() - timedelta(days=1)
    fechamento = abertura + timedelta(days=dias_ate_fechar)
    return {
        "data_abertura": abertura.isoformat(timespec="seconds"),
        "data_fechamento": fechamento.isoformat(timespec="seconds"),
    }


def _dias(quantidade: int = 1) -> list[str]:
    base = date.today() + timedelta(days=1)
    return [(base + timedelta(days=i)).isoformat() for i in range(quantidade)]


def _configurar(
    client: FlaskClient, headers: dict[str, str], dias: list[str], **janela: str
):
    payload = {"dias": dias, **(janela or _janela())}
    return client.put("/api/plantao/configuracao", json=payload, headers=headers)


def _headers_estagiarios(
    client: FlaskClient, app, quantidade: int
) -> list[dict[str, str]]:
    """Cria N estagiários de direito e devolve os headers autenticados de cada um."""
    headers = []
    for i in range(quantidade):
        email = f"estag{i}@gl.com"
        with app.app_context():
            criar_usuario(email, "estagpass123", "estag_direito", f"Estagiário {i}")
        headers.append(headers_para(client, email, "estagpass123"))
    return headers


def _marcar(client: FlaskClient, headers: dict[str, str], data: str):
    return client.post("/api/plantao/marcacoes", json={"data": data}, headers=headers)


def _pagina(client: FlaskClient, headers: dict[str, str]):
    return get_success_data(client.get("/api/plantao/", headers=headers))


def _vagas_do_dia(pagina: dict, data: str) -> int | None:
    return next(
        d["vagas_restantes"] for d in pagina["dias_abertos"] if d["data"] == data
    )


class TestConfiguracao:
    def test_get_sem_plantao_configurado(self, client, auth_headers):
        response = client.get("/api/plantao/configuracao", headers=auth_headers)
        assert response.status_code == 200

        data = get_success_data(response)
        assert data["data_abertura"] is None
        assert data["data_fechamento"] is None
        assert data["dias"] == []

    def test_put_cria_e_get_devolve(self, client, auth_headers):
        dias = _dias(2)
        response = _configurar(client, auth_headers, dias)
        assert response.status_code == 200

        data = get_success_data(
            client.get("/api/plantao/configuracao", headers=auth_headers)
        )
        assert data["dias"] == dias
        assert data["data_abertura"] is not None
        assert data["data_fechamento"] is not None

    def test_put_repetido_nao_cria_segundo_plantao(self, client, auth_headers, app):
        from sqlalchemy import func, select

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import plantao

        _configurar(client, auth_headers, _dias(1))
        _configurar(client, auth_headers, _dias(2))

        with app.app_context():
            session = get_session()
            total = session.execute(select(func.count()).select_from(plantao)).scalar()
        assert total == 1

    def test_diff_de_dias_desativa_reaproveita_e_cria(self, client, auth_headers, app):
        from sqlalchemy import select

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import dias_plantao

        a, b, c = _dias(3)

        _configurar(client, auth_headers, [a, b])
        with app.app_context():
            session = get_session()
            id_b = session.execute(
                select(dias_plantao.c.id).where(
                    dias_plantao.c.data == date.fromisoformat(b)
                )
            ).scalar()

        _configurar(client, auth_headers, [b, c])

        data = get_success_data(
            client.get("/api/plantao/configuracao", headers=auth_headers)
        )
        assert data["dias"] == [b, c]

        with app.app_context():
            session = get_session()
            linhas = {
                str(row.data): (row.id, row.status)
                for row in session.execute(select(dias_plantao)).all()
            }
        # `a` continua na tabela, apenas desativado (soft delete)
        assert linhas[a][1] is False
        # `b` manteve o mesmo registro, sem duplicar
        assert linhas[b][0] == id_b
        assert linhas[c][1] is True

    def test_dia_removido_e_readicionado_reativa_registro(
        self, client, auth_headers, app
    ):
        from sqlalchemy import func, select

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import dias_plantao

        (a,) = _dias(1)
        _configurar(client, auth_headers, [a])
        _configurar(client, auth_headers, [])
        _configurar(client, auth_headers, [a])

        with app.app_context():
            session = get_session()
            total = session.execute(
                select(func.count()).select_from(dias_plantao)
            ).scalar()
        assert total == 1

        data = get_success_data(
            client.get("/api/plantao/configuracao", headers=auth_headers)
        )
        assert data["dias"] == [a]

    def test_fechamento_anterior_a_abertura_e_recusado(self, client, auth_headers):
        abertura = datetime.now()
        response = _configurar(
            client,
            auth_headers,
            _dias(1),
            data_abertura=abertura.isoformat(timespec="seconds"),
            data_fechamento=(abertura - timedelta(hours=1)).isoformat(
                timespec="seconds"
            ),
        )
        assert response.status_code == 400

    def test_dias_repetidos_sao_recusados(self, client, auth_headers):
        (a,) = _dias(1)
        response = _configurar(client, auth_headers, [a, a])
        assert response.status_code == 400

    def test_papeis_sem_permissao_recebem_403(
        self, client, non_admin_auth_headers, prof_auth_headers, estagiario_auth_headers
    ):
        for headers in (
            non_admin_auth_headers,
            prof_auth_headers,
            estagiario_auth_headers,
        ):
            assert (
                client.get("/api/plantao/configuracao", headers=headers).status_code
                == 403
            )
            assert _configurar(client, headers, _dias(1)).status_code == 403

    def test_requer_autenticacao(self, client):
        assert client.get("/api/plantao/configuracao").status_code == 401
        assert client.put("/api/plantao/configuracao", json={}).status_code == 401


class TestMarcacoes:
    def test_marcar_dia_devolve_pagina_atualizada(self, client, auth_headers, app):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        response = _marcar(client, estagiario, dia)
        assert response.status_code == 201

        pagina = get_success_data(response)
        assert [m["data_marcada"] for m in pagina["meus_dias"]] == [dia]
        assert pagina["numero_plantao"] == 2
        assert pagina["limite_dias"] == 2

    def test_data_fora_dos_dias_abertos_e_recusada(self, client, auth_headers, app):
        dia, outro = _dias(2)
        _configurar(client, auth_headers, [dia])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        assert _marcar(client, estagiario, outro).status_code == 400

    def test_dia_repetido_e_recusado(self, client, auth_headers, app):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        assert _marcar(client, estagiario, dia).status_code == 201
        response = _marcar(client, estagiario, dia)
        assert response.status_code == 422
        assert response.json["error"]["code"] == "DIA_JA_MARCADO"

    def test_orientador_tem_limite_de_um_dia(
        self, client, auth_headers, non_admin_auth_headers
    ):
        dia, outro = _dias(2)
        _configurar(client, auth_headers, [dia, outro])

        pagina = _pagina(client, non_admin_auth_headers)
        assert pagina["limite_dias"] == 1

        assert _marcar(client, non_admin_auth_headers, dia).status_code == 201
        response = _marcar(client, non_admin_auth_headers, outro)
        assert response.status_code == 422
        assert response.json["error"]["code"] == "LIMITE_PLANTOES"

    def test_estagiario_tem_limite_de_dois_dias(self, client, auth_headers, app):
        a, b, c = _dias(3)
        _configurar(client, auth_headers, [a, b, c])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        assert _marcar(client, estagiario, a).status_code == 201
        assert _marcar(client, estagiario, b).status_code == 201
        response = _marcar(client, estagiario, c)
        assert response.status_code == 422
        assert response.json["error"]["code"] == "LIMITE_PLANTOES"

    def test_dia_lotado_e_recusado_quando_ha_outro_dia_livre(
        self, client, auth_headers, app
    ):
        lotado, livre = _dias(2)
        _configurar(client, auth_headers, [lotado, livre])
        estagiarios = _headers_estagiarios(client, app, 4)

        for headers in estagiarios[:3]:
            assert _marcar(client, headers, lotado).status_code == 201

        response = _marcar(client, estagiarios[3], lotado)
        assert response.status_code == 422
        assert response.json["error"]["code"] == "SEM_VAGAS"
        # ...mas o dia que ainda tem vaga continua disponível
        assert _marcar(client, estagiarios[3], livre).status_code == 201

    def test_overbooking_libera_quando_todos_os_dias_estao_lotados(
        self, client, auth_headers, app
    ):
        (unico,) = _dias(1)
        _configurar(client, auth_headers, [unico])
        estagiarios = _headers_estagiarios(client, app, 4)

        for headers in estagiarios[:3]:
            assert _marcar(client, headers, unico).status_code == 201

        # Sem a válvula de escape da v2, ninguém mais conseguiria marcar plantão.
        assert _marcar(client, estagiarios[3], unico).status_code == 201

    def test_limpar_marcacoes_reseta_contador(self, client, auth_headers, app):
        a, b = _dias(2)
        _configurar(client, auth_headers, [a, b])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        _marcar(client, estagiario, a)
        _marcar(client, estagiario, b)
        assert _pagina(client, estagiario)["numero_plantao"] == 3

        response = client.delete("/api/plantao/marcacoes", headers=estagiario)
        assert response.status_code == 200

        pagina = _pagina(client, estagiario)
        assert pagina["meus_dias"] == []
        # Na v2 o contador seguia crescendo porque as marcações apagadas
        # continuavam sendo somadas.
        assert pagina["numero_plantao"] == 1

    def test_limpar_marcacoes_devolve_a_vaga_ocupada(self, client, auth_headers, app):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])
        (estagiario,) = _headers_estagiarios(client, app, 1)

        cheio = _vagas_do_dia(_pagina(client, estagiario), dia)
        _marcar(client, estagiario, dia)
        assert _vagas_do_dia(_pagina(client, estagiario), dia) == cheio - 1

        client.delete("/api/plantao/marcacoes", headers=estagiario)
        # Na v2 a marcação apagada continuava ocupando a vaga para sempre.
        assert _vagas_do_dia(_pagina(client, estagiario), dia) == cheio

    def test_papel_sem_limite_de_vagas(self, client, auth_headers):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])

        pagina = _pagina(client, auth_headers)
        assert _vagas_do_dia(pagina, dia) is None
        assert next(d["tem_vaga"] for d in pagina["dias_abertos"] if d["data"] == dia)

    def test_janela_expirada_preserva_escala(
        self, client, auth_headers, non_admin_auth_headers
    ):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])
        _marcar(client, non_admin_auth_headers, dia)

        passado = datetime.now() - timedelta(days=10)
        _configurar(
            client,
            auth_headers,
            [dia],
            data_abertura=passado.isoformat(timespec="seconds"),
            data_fechamento=(passado + timedelta(days=1)).isoformat(timespec="seconds"),
        )

        pagina = _pagina(client, non_admin_auth_headers)
        assert pagina["plantao"]["aberto"] is False
        assert pagina["plantao"]["data_abertura"] is not None
        assert [d["data"] for d in pagina["dias_abertos"]] == [dia]
        assert [m["data_marcada"] for m in pagina["meus_dias"]] == [dia]

        # Idempotente: uma segunda leitura devolve o mesmo estado.
        assert _pagina(client, non_admin_auth_headers) == pagina

    def test_plantao_fechado_bloqueia_marcacao_mas_nao_admin(
        self, client, auth_headers, non_admin_auth_headers, app
    ):
        (dia,) = _dias(1)
        futuro = datetime.now() + timedelta(days=10)
        _configurar(
            client,
            auth_headers,
            [dia],
            data_abertura=futuro.isoformat(),
            data_fechamento=(futuro + timedelta(days=1)).isoformat(),
        )

        assert _pagina(client, non_admin_auth_headers)["pode_marcar"] is False
        assert _pagina(client, auth_headers)["pode_marcar"] is True

        response = _marcar(client, non_admin_auth_headers, dia)
        assert response.status_code == 422
        assert response.json["error"]["code"] == "PLANTAO_FECHADO"

        # admin e colab_proj marcam mesmo com o período fechado
        assert _marcar(client, auth_headers, dia).status_code == 201

    def test_escala_omite_usuario_inativo(self, client, auth_headers, app):
        from sqlalchemy import update

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import usuarios

        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])
        (estagiario,) = _headers_estagiarios(client, app, 1)
        _marcar(client, estagiario, dia)

        assert len(_pagina(client, auth_headers)["escala"]) == 1

        with app.app_context():
            session = get_session()
            session.execute(
                update(usuarios)
                .where(usuarios.c.email == "estag0@gl.com")
                .values(status=False)
            )
            session.commit()

        assert _pagina(client, auth_headers)["escala"] == []

    def test_requer_autenticacao(self, client):
        assert client.get("/api/plantao/").status_code == 401
        assert client.post("/api/plantao/marcacoes", json={}).status_code == 401
        assert client.delete("/api/plantao/marcacoes").status_code == 401


class TestUnidade:
    def test_configuracao_e_escala_isoladas_por_unidade(
        self, client, auth_headers, auth_headers_nl
    ):
        dia_bh, dia_nl = _dias(2)
        _configurar(client, auth_headers, [dia_bh])
        _configurar(client, auth_headers_nl, [dia_nl])

        config_bh = get_success_data(
            client.get("/api/plantao/configuracao", headers=auth_headers)
        )
        config_nl = get_success_data(
            client.get("/api/plantao/configuracao", headers=auth_headers_nl)
        )
        assert config_bh["dias"] == [dia_bh]
        assert config_nl["dias"] == [dia_nl]

        assert _marcar(client, auth_headers, dia_bh).status_code == 201

        pagina_bh = _pagina(client, auth_headers)
        assert [d["data"] for d in pagina_bh["dias_abertos"]] == [dia_bh]
        assert [m["data_marcada"] for m in pagina_bh["meus_dias"]] == [dia_bh]
        assert len(pagina_bh["escala"]) == 1

        # A mesma pessoa, na outra unidade, não vê a marcação nem o dia de BH.
        pagina_nl = _pagina(client, auth_headers_nl)
        assert [d["data"] for d in pagina_nl["dias_abertos"]] == [dia_nl]
        assert pagina_nl["meus_dias"] == []
        assert pagina_nl["escala"] == []

    def test_marcar_dia_aberto_em_outra_unidade_e_recusado(
        self, client, auth_headers, auth_headers_nl
    ):
        (dia,) = _dias(1)
        _configurar(client, auth_headers, [dia])

        # O dia pertence a BH; para Nova Lima ele simplesmente não foi aberto.
        response = _marcar(client, auth_headers_nl, dia)
        assert response.status_code == 422

    def test_encerramento_nao_encerra_plantao_de_outra_unidade(
        self, client, auth_headers, auth_headers_nl
    ):
        dia_bh, dia_nl = _dias(2)
        _configurar(client, auth_headers_nl, [dia_nl])
        _marcar(client, auth_headers_nl, dia_nl)

        passado = datetime.now() - timedelta(days=10)
        _configurar(
            client,
            auth_headers,
            [dia_bh],
            data_abertura=passado.isoformat(timespec="seconds"),
            data_fechamento=(passado + timedelta(days=1)).isoformat(timespec="seconds"),
        )
        _marcar(client, auth_headers, dia_bh)

        # A janela vencida não apaga a escala de nenhuma unidade.
        pagina_bh = _pagina(client, auth_headers)
        assert pagina_bh["plantao"]["aberto"] is False
        assert [d["data"] for d in pagina_bh["dias_abertos"]] == [dia_bh]
        assert [m["data_marcada"] for m in pagina_bh["meus_dias"]] == [dia_bh]

        # Nova Lima segue intacta: janela aberta, dia e marcação preservados.
        pagina_nl = _pagina(client, auth_headers_nl)
        assert pagina_nl["plantao"]["aberto"] is True
        assert [d["data"] for d in pagina_nl["dias_abertos"]] == [dia_nl]
        assert [m["data_marcada"] for m in pagina_nl["meus_dias"]] == [dia_nl]

    def test_limpar_marcacoes_so_apaga_as_da_unidade_ativa(
        self, client, auth_headers, auth_headers_nl
    ):
        dia_bh, dia_nl = _dias(2)
        _configurar(client, auth_headers, [dia_bh])
        _configurar(client, auth_headers_nl, [dia_nl])
        _marcar(client, auth_headers, dia_bh)
        _marcar(client, auth_headers_nl, dia_nl)

        assert (
            client.delete("/api/plantao/marcacoes", headers=auth_headers).status_code
            == 200
        )

        assert _pagina(client, auth_headers)["meus_dias"] == []
        assert [
            m["data_marcada"] for m in _pagina(client, auth_headers_nl)["meus_dias"]
        ] == [dia_nl]


class TestEscalas:
    def test_legado_inativo_consultavel_sem_reabrir(self, client, auth_headers, app):
        from sqlalchemy import insert, select
        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import plantao, dias_marcados_plantao, usuarios

        with app.app_context():
            session = get_session()
            uid = session.execute(
                select(usuarios.c.id).where(usuarios.c.email == "admin@gl.com")
            ).scalar_one()
            ident = session.execute(
                insert(plantao).values(unidade_id=1, nome="Legado", legado=True)
            ).lastrowid
            session.execute(
                insert(dias_marcados_plantao).values(
                    plantao_id=ident,
                    unidade_id=1,
                    id_usuario=uid,
                    status=False,
                    data_marcada=None,
                    confirmacao="ausencia",
                )
            )
            session.commit()
        pagina = self.pagina(client, auth_headers, ident)
        assert pagina["plantao"]["situacao"] == "legado"
        assert not pagina["pode_marcar"]
        assert pagina["escala"][0]["ativo"] is False
        assert pagina["escala"][0]["data"] is None
        assert pagina["escala"][0]["confirmacao"] == "ausencia"
        assert (
            client.post(
                f"/api/plantao/escalas/{ident}/cancelar", headers=auth_headers
            ).status_code
            == 400
        )
        assert (
            client.put(
                f"/api/plantao/configuracao?escala_id={ident}",
                json={"nome": "Novo", "dias": _dias(), **_janela()},
                headers=auth_headers,
            ).status_code
            == 400
        )

    def test_fechamento_preserva_confirmacao_cancelamento_retira_pendencias(
        self, client, auth_headers
    ):
        passado = datetime.now() - timedelta(days=10)
        dia = (date.today() - timedelta(days=1)).isoformat()
        escala = self.criar(
            client,
            auth_headers,
            dias=[dia],
            data_abertura=passado.isoformat(),
            data_fechamento=(passado + timedelta(days=1)).isoformat(),
        )
        ident = escala["id"]
        assert (
            client.post(
                f"/api/plantao/marcacoes?escala_id={ident}",
                json={"data": dia},
                headers=auth_headers,
            ).status_code
            == 201
        )
        pendencias = get_success_data(
            client.get(f"/api/presenca/confirmacao?data={dia}", headers=auth_headers)
        )["plantoes"]
        assert any(p["escala_id"] == ident for p in pendencias)
        assert (
            client.post(
                f"/api/plantao/escalas/{ident}/cancelar", headers=auth_headers
            ).status_code
            == 200
        )
        pendencias = get_success_data(
            client.get(f"/api/presenca/confirmacao?data={dia}", headers=auth_headers)
        )["plantoes"]
        assert not any(p["escala_id"] == ident for p in pendencias)
        assert len(self.pagina(client, auth_headers, ident)["escala"]) == 1

    def criar(self, client, headers, nome="Escala nova", **kwargs):
        payload = {"nome": nome, "dias": _dias(3), **_janela(), **kwargs}
        response = client.post("/api/plantao/escalas", json=payload, headers=headers)
        assert response.status_code == 201, response.json
        return get_success_data(response)

    def pagina(self, client, headers, ident):
        return get_success_data(
            client.get(f"/api/plantao/?escala_id={ident}", headers=headers)
        )

    def test_periodos_independentes_limite_e_historico(
        self, client, auth_headers, non_admin_auth_headers
    ):
        a = self.criar(client, auth_headers, "Setembro")
        dia = a["dias"][0]
        url = f"/api/plantao/marcacoes?escala_id={a['id']}"
        assert (
            client.post(
                url, json={"data": dia}, headers=non_admin_auth_headers
            ).status_code
            == 201
        )
        b = self.criar(client, auth_headers, "Outubro")
        assert (
            client.post(
                f"/api/plantao/marcacoes?escala_id={b['id']}",
                json={"data": dia},
                headers=non_admin_auth_headers,
            ).status_code
            == 201
        )
        assert (
            len(self.pagina(client, non_admin_auth_headers, a["id"])["meus_dias"]) == 1
        )
        assert (
            len(self.pagina(client, non_admin_auth_headers, b["id"])["meus_dias"]) == 1
        )
        escalas = get_success_data(
            client.get("/api/plantao/escalas", headers=auth_headers)
        )
        assert [s["nome"] for s in escalas] == ["Outubro", "Setembro"]
        assert (
            self.pagina(client, auth_headers, a["id"])["historico"][-1]["acao"]
            == "inscrever"
        )

    def test_limites_exatos_de_inscricao_e_fechamento_sem_apagar(
        self, client, auth_headers, non_admin_auth_headers, monkeypatch
    ):
        import gestaolegal.services.plantao_service as service

        inicio = datetime(2026, 9, 1, 8)
        fim = datetime(2026, 9, 5, 18)
        escala = self.criar(
            client,
            auth_headers,
            data_abertura=inicio.isoformat(),
            data_fechamento=fim.isoformat(),
        )
        ident = escala["id"]
        url = f"/api/plantao/marcacoes?escala_id={ident}"
        monkeypatch.setattr(
            service, "agora_brasilia", lambda: inicio - timedelta(seconds=1)
        )
        assert (
            self.pagina(client, non_admin_auth_headers, ident)["plantao"]["aberto"]
            is False
        )
        assert (
            client.post(
                url, json={"data": escala["dias"][0]}, headers=non_admin_auth_headers
            ).status_code
            == 422
        )
        monkeypatch.setattr(service, "agora_brasilia", lambda: inicio)
        assert (
            client.post(
                url, json={"data": escala["dias"][0]}, headers=non_admin_auth_headers
            ).status_code
            == 201
        )
        monkeypatch.setattr(service, "agora_brasilia", lambda: fim)
        pagina = self.pagina(client, non_admin_auth_headers, ident)
        assert pagina["plantao"]["aberto"] is False
        assert len(pagina["escala"]) == len(pagina["meus_dias"]) == 1
        assert len(pagina["dias_abertos"]) == 3
        assert client.delete(url, headers=non_admin_auth_headers).status_code == 422
        assert self.pagina(client, non_admin_auth_headers, ident) == pagina
        assert client.delete(url, headers=auth_headers).status_code == 200
        assert (
            self.pagina(client, auth_headers, ident)["historico"][-1]["detalhes"][
                "fora_do_prazo"
            ]
            is True
        )

    def test_cancelar_preserva_dados_e_bloqueia_alteracoes(self, client, auth_headers):
        escala = self.criar(client, auth_headers)
        ident = escala["id"]
        url = f"/api/plantao/marcacoes?escala_id={ident}"
        assert (
            client.post(
                url, json={"data": escala["dias"][0]}, headers=auth_headers
            ).status_code
            == 201
        )
        assert (
            client.post(
                f"/api/plantao/escalas/{ident}/cancelar", headers=auth_headers
            ).status_code
            == 200
        )
        pagina = self.pagina(client, auth_headers, ident)
        assert pagina["plantao"]["situacao"] == "cancelada"
        assert len(pagina["escala"]) == 1
        assert not pagina["pode_marcar"]
        assert client.delete(url, headers=auth_headers).status_code == 422
        assert (
            client.put(
                f"/api/plantao/configuracao?escala_id={ident}",
                json={"nome": "alterado", "dias": _dias(), **_janela()},
                headers=auth_headers,
            ).status_code
            == 400
        )

    def test_id_de_outra_unidade_e_inexistente_bloqueados(
        self, client, auth_headers, auth_headers_nl
    ):
        escala = self.criar(client, auth_headers)
        ident = escala["id"]
        for url in (
            f"/api/plantao/?escala_id={ident}",
            f"/api/plantao/configuracao?escala_id={ident}",
        ):
            assert client.get(url, headers=auth_headers_nl).status_code == 404
        assert (
            client.post(
                f"/api/plantao/escalas/{ident}/cancelar", headers=auth_headers_nl
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/api/plantao/marcacoes?escala_id={ident}",
                json={"data": escala["dias"][0]},
                headers=auth_headers_nl,
            ).status_code
            == 404
        )
        assert (
            client.get(
                "/api/plantao/?escala_id=999999", headers=auth_headers
            ).status_code
            == 404
        )
        assert (
            get_success_data(
                client.get("/api/plantao/escalas", headers=auth_headers_nl)
            )
            == []
        )

    def test_remover_dia_inscrito_recusado_sem_alterar_configuracao(
        self, client, auth_headers
    ):
        escala = self.criar(client, auth_headers)
        ident = escala["id"]
        client.post(
            f"/api/plantao/marcacoes?escala_id={ident}",
            json={"data": escala["dias"][0]},
            headers=auth_headers,
        )
        response = client.put(
            f"/api/plantao/configuracao?escala_id={ident}",
            json={"nome": "Não salvar", "dias": [], **_janela()},
            headers=auth_headers,
        )
        assert response.status_code == 400
        atual = get_success_data(
            client.get(
                f"/api/plantao/configuracao?escala_id={ident}", headers=auth_headers
            )
        )
        assert atual == escala

    def test_criacao_exige_permissao_nome_e_dias(
        self, client, auth_headers, non_admin_auth_headers
    ):
        payload = {"nome": "Escala", "dias": _dias(), **_janela()}
        assert (
            client.post(
                "/api/plantao/escalas", json=payload, headers=non_admin_auth_headers
            ).status_code
            == 403
        )
        for changes in ({"nome": " "}, {"dias": []}):
            assert (
                client.post(
                    "/api/plantao/escalas", json=payload | changes, headers=auth_headers
                ).status_code
                == 400
            )
