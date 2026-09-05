"""Arquivos gerais (módulo "Arquivos" da v2)."""

import os
from io import BytesIO

import pytest
from flask.testing import FlaskClient

from tests.api.conftest import clean_tables, get_success_data


@pytest.fixture(autouse=True)
def arquivos_dir(tmp_path, monkeypatch, app):
    """Aponta a raiz privada para um tmpdir; o service resolve a categoria."""
    monkeypatch.setitem(app.config, "PRIVATE_FILES_ROOT", str(tmp_path))
    destino = tmp_path / "arquivos"
    destino.mkdir()
    with app.app_context():
        clean_tables("arquivos")
    return destino


def _criar(client: FlaskClient, headers: dict[str, str], titulo="Regimento", nome="regimento.docx", conteudo=b"conteudo", descricao="Descrição do regimento"):
    data = {"titulo": titulo, "descricao": descricao, "arquivo": (BytesIO(conteudo), nome)}
    return client.post("/api/arquivo/", data=data, headers=headers, content_type="multipart/form-data")


class TestCriar:
    def test_admin_cria(self, client, auth_headers, arquivos_dir):
        response = _criar(client, auth_headers)
        assert response.status_code == 201
        data = get_success_data(response)
        assert data["titulo"] == "Regimento"
        assert data["nome"] == "regimento.docx"
        assert data["descricao"] == "Descrição do regimento"
        assert data["id_criado_por"] is not None
        assert os.path.exists(data["caminho"])
        assert len(os.listdir(arquivos_dir)) == 1

    def test_professor_cria(self, client, prof_auth_headers):
        assert _criar(client, prof_auth_headers).status_code == 201

    def test_estagiario_nao_cria(self, client, estagiario_auth_headers):
        response = _criar(client, estagiario_auth_headers)
        assert response.status_code == 403
        assert "permissão" in response.get_json()["error"]["message"]

    def test_sem_arquivo(self, client, auth_headers):
        response = client.post("/api/arquivo/", data={"titulo": "X"}, headers=auth_headers, content_type="multipart/form-data")
        assert response.status_code == 400
        assert "adicionar um arquivo" in response.get_json()["error"]["message"]

    def test_sem_titulo(self, client, auth_headers, arquivos_dir):
        response = _criar(client, auth_headers, titulo="  ")
        assert response.status_code == 400
        assert "título" in response.get_json()["error"]["message"]
        assert os.listdir(arquivos_dir) == []

    def test_titulo_longo(self, client, auth_headers):
        response = _criar(client, auth_headers, titulo="a" * 151)
        assert response.status_code == 400

    def test_aceita_qualquer_tipo(self, client, auth_headers):
        assert _criar(client, auth_headers, nome="planilha.xlsx").status_code == 201
        assert _criar(client, auth_headers, nome="foto.png").status_code == 201


class TestListar:
    def test_lista_paginada_com_busca(self, client, auth_headers, estagiario_auth_headers):
        _criar(client, auth_headers, titulo="Regimento interno")
        _criar(client, auth_headers, titulo="Modelo de petição", descricao="Petição inicial")
        _criar(client, auth_headers, titulo="Calendário")

        data = get_success_data(client.get("/api/arquivo/", headers=estagiario_auth_headers))
        assert data["total"] == 3
        assert data["items"][0]["titulo"] == "Calendário"  # mais recente primeiro
        assert data["items"][0]["criado_por"]

        data = get_success_data(client.get("/api/arquivo/?search=petição", headers=auth_headers))
        assert [i["titulo"] for i in data["items"]] == ["Modelo de petição"]

        data = get_success_data(client.get("/api/arquivo/?per_page=2&page=2", headers=auth_headers))
        assert len(data["items"]) == 1 and data["total_pages"] == 2

    def test_busca_por_id(self, client, auth_headers):
        arquivo_id = get_success_data(_criar(client, auth_headers))["id"]
        data = get_success_data(client.get(f"/api/arquivo/{arquivo_id}", headers=auth_headers))
        assert data["id"] == arquivo_id

    def test_inexistente(self, client, auth_headers):
        assert client.get("/api/arquivo/9999", headers=auth_headers).status_code == 404


class TestEditar:
    def test_edita_so_texto(self, client, auth_headers, arquivos_dir):
        criado = get_success_data(_criar(client, auth_headers))
        response = client.put(
            f"/api/arquivo/{criado['id']}",
            data={"titulo": "Novo título", "descricao": ""},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        data = get_success_data(response)
        assert data["titulo"] == "Novo título"
        assert data["descricao"] is None
        assert data["caminho"] == criado["caminho"]
        assert len(os.listdir(arquivos_dir)) == 1

    def test_substitui_arquivo(self, client, auth_headers, arquivos_dir):
        criado = get_success_data(_criar(client, auth_headers))
        response = client.put(
            f"/api/arquivo/{criado['id']}",
            data={"titulo": "Regimento", "arquivo": (BytesIO(b"novo"), "regimento_v2.pdf")},
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        data = get_success_data(response)
        assert data["nome"] == "regimento_v2.pdf"
        assert data["caminho"] != criado["caminho"]
        assert not os.path.exists(criado["caminho"])
        assert len(os.listdir(arquivos_dir)) == 1

    def test_colab_externo_edita(self, client, auth_headers, app):
        from tests.api.conftest import criar_usuario, headers_para

        with app.app_context():
            criar_usuario("colabext@gl.com", "senha123!", "colab_ext", "Colab Externo")
        headers = headers_para(client, "colabext@gl.com", "senha123!")
        criado = get_success_data(_criar(client, auth_headers))
        response = client.put(
            f"/api/arquivo/{criado['id']}", data={"titulo": "Editado"}, headers=headers, content_type="multipart/form-data"
        )
        assert response.status_code == 200


class TestExcluir:
    def test_admin_exclui_e_apaga_do_disco(self, client, auth_headers, arquivos_dir):
        criado = get_success_data(_criar(client, auth_headers))
        assert client.delete(f"/api/arquivo/{criado['id']}", headers=auth_headers).status_code == 200
        assert client.get(f"/api/arquivo/{criado['id']}", headers=auth_headers).status_code == 404
        assert os.listdir(arquivos_dir) == []

    def test_colab_externo_nao_exclui(self, client, auth_headers, app):
        from tests.api.conftest import criar_usuario, headers_para

        with app.app_context():
            criar_usuario("colabext2@gl.com", "senha123!", "colab_ext", "Colab Externo")
        headers = headers_para(client, "colabext2@gl.com", "senha123!")
        criado = get_success_data(_criar(client, auth_headers))
        assert client.delete(f"/api/arquivo/{criado['id']}", headers=headers).status_code == 403


class TestDownload:
    def test_download_com_nome_original(self, client, auth_headers, estagiario_auth_headers):
        criado = get_success_data(_criar(client, auth_headers, conteudo=b"abc123", nome="ata reunião.txt"))
        response = client.get(f"/api/arquivo/{criado['id']}/download", headers=estagiario_auth_headers)
        assert response.status_code == 200
        assert response.data == b"abc123"
        assert "reuni" in response.headers["Content-Disposition"]

    def test_download_sem_login(self, client, auth_headers):
        criado = get_success_data(_criar(client, auth_headers))
        assert client.get(f"/api/arquivo/{criado['id']}/download").status_code == 401
