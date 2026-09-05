from datetime import date, datetime, time, timedelta

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, criar_usuario, get_success_data, headers_para

TABELAS = ("registro_entrada", "dias_marcados_plantao", "dias_plantao", "plantao")


@pytest.fixture(autouse=True)
def _reset(app):
    with app.app_context():
        clean_tables(*TABELAS)
    yield


def _registrar(client: FlaskClient, headers: dict[str, str], hora: str):
    return client.post("/api/presenca/registro", json={"hora": hora}, headers=headers)


def _estado(client: FlaskClient, headers: dict[str, str]):
    return get_success_data(client.get("/api/presenca/registro", headers=headers))


def _confirmacao(client: FlaskClient, headers: dict[str, str], data: str | None = None):
    url = "/api/presenca/confirmacao"
    if data:
        url = f"{url}?data={data}"
    return get_success_data(client.get(url, headers=headers))


def _inserir_registro(
    app,
    id_usuario: int,
    entrada: datetime,
    saida: datetime | None = None,
    status: bool = True,
    confirmacao: str = "aberto",
    unidade_id: int = 1,
) -> int:
    from sqlalchemy import insert

    from gestaolegal.database.session import get_session
    from gestaolegal.database.tables import registro_entrada

    with app.app_context():
        session = get_session()
        result = session.execute(
            insert(registro_entrada).values(
                data_entrada=entrada,
                data_saida=saida or datetime.combine(entrada.date(), time(23, 59, 59)),
                id_usuario=id_usuario,
                status=status,
                confirmacao=confirmacao,
                unidade_id=unidade_id,
            )
        )
        session.commit()
        return result.lastrowid


def _id_do_usuario(app, email: str) -> int:
    from sqlalchemy import select

    from gestaolegal.database.session import get_session
    from gestaolegal.database.tables import usuarios

    with app.app_context():
        session = get_session()
        return session.execute(
            select(usuarios.c.id).where(usuarios.c.email == email)
        ).scalar()


class TestRegistroDePonto:
    def test_sem_historico_a_proxima_acao_e_entrada(self, client, auth_headers):
        assert _estado(client, auth_headers)["status_presenca"] == "entrada"

    def test_ciclo_entrada_saida_entrada(self, client, auth_headers, app):
        response = _registrar(client, auth_headers, "09:00")
        assert response.status_code == 200
        assert get_success_data(response)["acao"] == "entrada"
        assert _estado(client, auth_headers)["status_presenca"] == "saida"

        response = _registrar(client, auth_headers, "12:30")
        assert get_success_data(response)["acao"] == "saida"

        estado = _estado(client, auth_headers)
        assert estado["status_presenca"] == "entrada"
        assert estado["registro_aberto"] is None

        # Um novo registro no mesmo dia é permitido (comportamento da v2).
        assert get_success_data(_registrar(client, auth_headers, "14:00"))["acao"] == "entrada"

    def test_saida_grava_o_horario_informado(self, client, auth_headers, app):
        from sqlalchemy import select

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import registro_entrada

        _registrar(client, auth_headers, "09:00")
        _registrar(client, auth_headers, "12:30")

        with app.app_context():
            session = get_session()
            row = session.execute(select(registro_entrada)).first()

        assert row.data_entrada.strftime("%H:%M") == "09:00"
        assert row.data_saida.strftime("%H:%M") == "12:30"
        assert row.status is False

    @pytest.mark.parametrize("payload", [{"hora": "25:00"}, {"hora": "9h"}, {}])
    def test_hora_invalida_e_recusada(self, client, auth_headers, payload):
        response = client.post(
            "/api/presenca/registro", json=payload, headers=auth_headers
        )
        assert response.status_code == 400

    def test_registro_aberto_de_outro_mes_e_fechado(self, client, auth_headers, app):
        id_admin = _id_do_usuario(app, "admin@gl.com")
        # A v2 comparava dia, mês e ano separadamente e deixava esse caso passar.
        registro_id = _inserir_registro(
            app, id_admin, datetime.now() - timedelta(days=45)
        )

        assert _estado(client, auth_headers)["status_presenca"] == "entrada"

        from sqlalchemy import select

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import registro_entrada

        with app.app_context():
            session = get_session()
            status = session.execute(
                select(registro_entrada.c.status).where(
                    registro_entrada.c.id == registro_id
                )
            ).scalar()
        assert status is False

    def test_qualquer_papel_autenticado_pode_registrar(
        self, client, non_admin_auth_headers, estagiario_auth_headers
    ):
        for headers in (non_admin_auth_headers, estagiario_auth_headers):
            assert client.get("/api/presenca/registro", headers=headers).status_code == 200
            assert _registrar(client, headers, "08:00").status_code == 200

    def test_requer_autenticacao(self, client):
        assert client.get("/api/presenca/registro").status_code == 401
        assert client.post("/api/presenca/registro", json={"hora": "08:00"}).status_code == 401


class TestConfirmacao:
    def test_lista_apenas_registros_fechados_e_pendentes(self, client, auth_headers, app):
        id_admin = _id_do_usuario(app, "admin@gl.com")
        ontem = datetime.combine(date.today() - timedelta(days=1), time(9, 0))

        pendente = _inserir_registro(
            app, id_admin, ontem, saida=ontem + timedelta(hours=3), status=False
        )
        # Em curso: ainda não é conferível
        _inserir_registro(app, id_admin, ontem + timedelta(minutes=1), status=True)
        # Já conferido
        _inserir_registro(
            app,
            id_admin,
            ontem + timedelta(minutes=2),
            saida=ontem + timedelta(hours=4),
            status=False,
            confirmacao="confirmar",
        )
        # Outro dia
        _inserir_registro(
            app,
            id_admin,
            ontem - timedelta(days=3),
            saida=ontem - timedelta(days=3) + timedelta(hours=1),
            status=False,
        )

        data = _confirmacao(client, auth_headers, ontem.date().isoformat())
        assert [p["id"] for p in data["presencas"]] == [pendente]

    def test_omite_usuario_inativo(self, client, auth_headers, app):
        with app.app_context():
            id_usuario = criar_usuario(
                "inativo@gl.com", "senha123456", "estag_direito", "Inativo", status=False
            )
        ontem = datetime.combine(date.today() - timedelta(days=1), time(9, 0))
        _inserir_registro(
            app, id_usuario, ontem, saida=ontem + timedelta(hours=2), status=False
        )

        data = _confirmacao(client, auth_headers, ontem.date().isoformat())
        assert data["presencas"] == []

    def test_omite_marcacao_de_plantao_apagada(self, client, auth_headers, app):
        from sqlalchemy import insert

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import dias_marcados_plantao

        id_admin = _id_do_usuario(app, "admin@gl.com")
        ontem = date.today() - timedelta(days=1)

        with app.app_context():
            session = get_session()
            ativa = session.execute(
                insert(dias_marcados_plantao).values(
                    data_marcada=ontem,
                    id_usuario=id_admin,
                    confirmacao="aberto",
                    status=True,
                    unidade_id=1,
                )
            ).lastrowid
            # Marcação apagada pelo botão "Editar": a v2 continuava listando
            session.execute(
                insert(dias_marcados_plantao).values(
                    data_marcada=ontem,
                    id_usuario=id_admin,
                    confirmacao="aberto",
                    status=False,
                    unidade_id=1,
                )
            )
            session.commit()

        data = _confirmacao(client, auth_headers, ontem.isoformat())
        assert [p["id"] for p in data["plantoes"]] == [ativa]

    @pytest.mark.parametrize(
        "weekday_referencia,dias_esperados",
        [(0, 3), (6, 2), (2, 1)],
        ids=["segunda_volta_para_sexta", "domingo_volta_para_sexta", "quarta_volta_um_dia"],
    )
    def test_data_padrao_e_o_dia_util_anterior(
        self, client, auth_headers, monkeypatch, weekday_referencia, dias_esperados
    ):
        import gestaolegal.utils.tempo as tempo

        # 2026-08-17 é uma segunda-feira; ajusta para o dia da semana pedido.
        referencia = date(2026, 8, 17) + timedelta(days=weekday_referencia)
        assert referencia.weekday() == weekday_referencia
        monkeypatch.setattr(tempo, "hoje_brasilia", lambda: referencia)

        data = _confirmacao(client, auth_headers)
        assert data["data"] == (referencia - timedelta(days=dias_esperados)).isoformat()

    def test_salvar_em_lote_remove_itens_da_pendencia(self, client, auth_headers, app):
        from sqlalchemy import insert

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import dias_marcados_plantao

        id_admin = _id_do_usuario(app, "admin@gl.com")
        ontem_data = date.today() - timedelta(days=1)
        ontem = datetime.combine(ontem_data, time(9, 0))

        presenca_id = _inserir_registro(
            app, id_admin, ontem, saida=ontem + timedelta(hours=3), status=False
        )
        with app.app_context():
            session = get_session()
            plantao_id = session.execute(
                insert(dias_marcados_plantao).values(
                    data_marcada=ontem_data,
                    id_usuario=id_admin,
                    confirmacao="aberto",
                    status=True,
                    unidade_id=1,
                )
            ).lastrowid
            session.commit()

        response = client.post(
            "/api/presenca/confirmacao",
            json={
                "presencas": [{"id": presenca_id, "confirmacao": "confirmar"}],
                "plantoes": [{"id": plantao_id, "confirmacao": "ausencia"}],
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert get_success_data(response) == {
            "presencas_atualizadas": 1,
            "plantoes_atualizados": 1,
        }

        data = _confirmacao(client, auth_headers, ontem_data.isoformat())
        assert data["presencas"] == []
        assert data["plantoes"] == []

    def test_confirmacao_invalida_e_recusada(self, client, auth_headers):
        response = client.post(
            "/api/presenca/confirmacao",
            json={"presencas": [{"id": 1, "confirmacao": "talvez"}]},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_id_inexistente_devolve_404(self, client, auth_headers):
        response = client.post(
            "/api/presenca/confirmacao",
            json={"presencas": [{"id": 9999, "confirmacao": "confirmar"}]},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_data_invalida_e_recusada(self, client, auth_headers):
        response = client.get(
            "/api/presenca/confirmacao?data=14-08-2026", headers=auth_headers
        )
        assert response.status_code == 400

    def test_professor_e_colaborador_de_projeto_tem_acesso(
        self, client, prof_auth_headers, app
    ):
        assert client.get(
            "/api/presenca/confirmacao", headers=prof_auth_headers
        ).status_code == 200

        with app.app_context():
            criar_usuario("colabproj@gl.com", "colabpass123", "colab_proj", "Colab")
        headers = headers_para(client, "colabproj@gl.com", "colabpass123")
        assert client.get("/api/presenca/confirmacao", headers=headers).status_code == 200

    def test_papeis_sem_permissao_recebem_403(
        self, client, non_admin_auth_headers, estagiario_auth_headers
    ):
        for headers in (non_admin_auth_headers, estagiario_auth_headers):
            assert client.get(
                "/api/presenca/confirmacao", headers=headers
            ).status_code == 403
            assert client.post(
                "/api/presenca/confirmacao", json={}, headers=headers
            ).status_code == 403

    def test_requer_autenticacao(self, client):
        assert client.get("/api/presenca/confirmacao").status_code == 401
        assert client.post("/api/presenca/confirmacao", json={}).status_code == 401


class TestUnidade:
    def test_ponto_aberto_em_uma_unidade_nao_aparece_na_outra(
        self, client, auth_headers, auth_headers_nl
    ):
        assert get_success_data(_registrar(client, auth_headers, "09:00"))["acao"] == "entrada"

        # A mesma pessoa, em Nova Lima, ainda não bateu entrada por lá.
        estado_nl = _estado(client, auth_headers_nl)
        assert estado_nl["status_presenca"] == "entrada"
        assert estado_nl["registro_aberto"] is None

        assert (
            get_success_data(_registrar(client, auth_headers_nl, "10:00"))["acao"]
            == "entrada"
        )

        # A saída em BH não fecha o registro que está em curso em Nova Lima.
        assert get_success_data(_registrar(client, auth_headers, "12:00"))["acao"] == "saida"
        assert _estado(client, auth_headers)["registro_aberto"] is None
        assert _estado(client, auth_headers_nl)["status_presenca"] == "saida"

    def test_conferencia_lista_so_a_unidade_ativa(
        self, client, auth_headers, auth_headers_nl, app
    ):
        ontem = date.today() - timedelta(days=1)
        admin_id = _id_do_usuario(app, "admin@gl.com")
        entrada = datetime.combine(ontem, time(9, 0))

        registro_bh = _inserir_registro(
            app, admin_id, entrada, saida=entrada + timedelta(hours=3), status=False
        )
        registro_nl = _inserir_registro(
            app,
            admin_id,
            entrada,
            saida=entrada + timedelta(hours=3),
            status=False,
            unidade_id=2,
        )

        dia = ontem.isoformat()
        assert [p["id"] for p in _confirmacao(client, auth_headers, dia)["presencas"]] == [
            registro_bh
        ]
        assert [
            p["id"] for p in _confirmacao(client, auth_headers_nl, dia)["presencas"]
        ] == [registro_nl]

    def test_confirmar_registro_de_outra_unidade_responde_404(
        self, client, auth_headers_nl, app
    ):
        ontem = date.today() - timedelta(days=1)
        admin_id = _id_do_usuario(app, "admin@gl.com")
        entrada = datetime.combine(ontem, time(9, 0))
        registro_bh = _inserir_registro(
            app, admin_id, entrada, saida=entrada + timedelta(hours=3), status=False
        )

        response = client.post(
            "/api/presenca/confirmacao",
            json={
                "presencas": [{"id": registro_bh, "confirmacao": "confirmar"}],
                "plantoes": [],
            },
            headers=auth_headers_nl,
        )
        assert response.status_code == 404

    def test_plantao_de_outra_unidade_nao_entra_na_conferencia(
        self, client, auth_headers, auth_headers_nl, app
    ):
        from sqlalchemy import insert

        from gestaolegal.database.session import get_session
        from gestaolegal.database.tables import dias_marcados_plantao

        ontem = date.today() - timedelta(days=1)
        admin_id = _id_do_usuario(app, "admin@gl.com")
        with app.app_context():
            session = get_session()
            marcacao_bh = session.execute(
                insert(dias_marcados_plantao).values(
                    data_marcada=ontem,
                    id_usuario=admin_id,
                    confirmacao="aberto",
                    status=True,
                    unidade_id=1,
                )
            ).lastrowid
            session.commit()

        dia = ontem.isoformat()
        assert [p["id"] for p in _confirmacao(client, auth_headers, dia)["plantoes"]] == [
            marcacao_bh
        ]
        assert _confirmacao(client, auth_headers_nl, dia)["plantoes"] == []

        response = client.post(
            "/api/presenca/confirmacao",
            json={
                "presencas": [],
                "plantoes": [{"id": marcacao_bh, "confirmacao": "confirmar"}],
            },
            headers=auth_headers_nl,
        )
        assert response.status_code == 404
