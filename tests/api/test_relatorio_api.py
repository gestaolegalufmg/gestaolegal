from datetime import date, datetime, time

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data

TABELAS = ("registro_entrada", "dias_marcados_plantao")


@pytest.fixture(autouse=True)
def _reset(app):
    with app.app_context():
        clean_tables(*TABELAS)
    yield


def _inserir_presenca(app, id_usuario: int, dia: date, entrada: str, saida: str, confirmacao="aberto"):
    from sqlalchemy import insert

    from gestaolegal.database.session import get_session
    from gestaolegal.database.tables import registro_entrada

    h_e, m_e = (int(x) for x in entrada.split(":"))
    h_s, m_s = (int(x) for x in saida.split(":"))
    with app.app_context():
        session = get_session()
        session.execute(
            insert(registro_entrada).values(
                data_entrada=datetime.combine(dia, time(h_e, m_e)),
                data_saida=datetime.combine(dia, time(h_s, m_s)),
                id_usuario=id_usuario,
                status=False,
                confirmacao=confirmacao,
            )
        )
        session.commit()


def _inserir_plantao(app, id_usuario: int, dia: date, status=True, confirmacao="aberto"):
    from sqlalchemy import insert

    from gestaolegal.database.session import get_session
    from gestaolegal.database.tables import dias_marcados_plantao

    with app.app_context():
        session = get_session()
        session.execute(
            insert(dias_marcados_plantao).values(
                data_marcada=dia,
                id_usuario=id_usuario,
                status=status,
                confirmacao=confirmacao,
            )
        )
        session.commit()


def _horarios(client: FlaskClient, headers, inicio: str, fim: str, usuarios: str | None = None):
    url = f"/api/relatorio/horarios?data_inicio={inicio}&data_final={fim}"
    if usuarios:
        url += f"&usuarios={usuarios}"
    return client.get(url, headers=headers)


class TestRelatorioHorarios:
    def test_lista_presencas_e_plantoes_do_periodo(self, client, auth_headers, non_admin_auth_headers, app):
        _inserir_presenca(app, 1, date(2024, 3, 4), "08:00", "12:00", "confirmar")
        _inserir_presenca(app, 2, date(2024, 3, 5), "13:00", "17:30")
        _inserir_presenca(app, 1, date(2024, 4, 1), "08:00", "12:00")  # fora do período
        _inserir_plantao(app, 1, date(2024, 3, 6))
        _inserir_plantao(app, 2, date(2024, 3, 6), status=False)  # marcação apagada
        _inserir_plantao(app, 2, date(2024, 3, 31))  # fora do período

        data = get_success_data(_horarios(client, auth_headers, "2024-03-01", "2024-03-30"))

        assert data["total_presencas"] == 2
        assert data["total_plantoes"] == 1
        primeira = data["presencas"][0]
        assert primeira["data"] == "2024-03-04"
        assert primeira["entrada"] == "08:00"
        assert primeira["saida"] == "12:00"
        assert primeira["confirmacao"] == "confirmar"
        assert primeira["nome"]
        assert data["plantoes"][0]["data"] == "2024-03-06"
        assert data["plantoes"][0]["id_usuario"] == 1

    def test_filtra_por_usuarios(self, client, auth_headers, non_admin_auth_headers, app):
        _inserir_presenca(app, 1, date(2024, 3, 4), "08:00", "12:00")
        _inserir_presenca(app, 2, date(2024, 3, 4), "08:00", "12:00")
        _inserir_plantao(app, 1, date(2024, 3, 6))
        _inserir_plantao(app, 2, date(2024, 3, 6))

        data = get_success_data(_horarios(client, auth_headers, "2024-03-01", "2024-03-30", "2"))
        assert [p["id_usuario"] for p in data["presencas"]] == [2]
        assert [p["id_usuario"] for p in data["plantoes"]] == [2]

        # "todos" e lista vazia não filtram.
        data = get_success_data(_horarios(client, auth_headers, "2024-03-01", "2024-03-30", "todos"))
        assert data["total_presencas"] == 2

    def test_inclui_o_ultimo_dia_inteiro(self, client, auth_headers, app):
        _inserir_presenca(app, 1, date(2024, 3, 30), "18:00", "22:00")
        data = get_success_data(_horarios(client, auth_headers, "2024-03-01", "2024-03-30"))
        assert data["total_presencas"] == 1

    def test_usuarios_invalidos(self, client, auth_headers):
        response = _horarios(client, auth_headers, "2024-03-01", "2024-03-30", "a,b")
        assert response.status_code == 400

    def test_datas_obrigatorias(self, client, auth_headers):
        response = client.get("/api/relatorio/horarios?data_inicio=2024-01-01", headers=auth_headers)
        assert response.status_code == 400

    def test_estagiario_nao_acessa(self, client, estagiario_auth_headers):
        response = _horarios(client, estagiario_auth_headers, "2024-03-01", "2024-03-30")
        assert response.status_code == 403

    def test_orientador_acessa(self, client, non_admin_auth_headers):
        response = _horarios(client, non_admin_auth_headers, "2024-03-01", "2024-03-30")
        assert response.status_code == 200
