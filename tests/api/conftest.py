import os
import tempfile

# Use a temporary directory for file uploads in tests
TEST_UPLOAD_DIR = tempfile.mkdtemp()

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ADMIN_EMAIL"] = "admin@test.com"
os.environ["ADMIN_PASSWORD"] = "123456"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_NAME"] = "test_db"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["STATIC_ROOT_DIR"] = TEST_UPLOAD_DIR

from collections.abc import Generator
from datetime import datetime
from typing import Any

import bcrypt
import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine, orm, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

import gestaolegal.database.session as db_session_module
from gestaolegal import create_app
from gestaolegal.database.tables import metadata

TEST_ADMIN_EMAIL = "admin@gl.com"
TEST_ADMIN_PASSWORD = "123456"

test_engine: Engine = create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture(scope="session", autouse=True)
def _setup_db_session_module() -> None:
    db_session_module.engine = test_engine
    db_session_module.SessionLocal = orm.sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )


@pytest.fixture(scope="session")
def app() -> Generator[Flask, None, None]:
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        metadata.create_all(bind=test_engine)

    yield app

    with app.app_context():
        metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def clean_tables(*table_names: str) -> None:
    from gestaolegal.database.tables import metadata
    
    session = db_session_module.get_session()
    try:
        for table_name in table_names:
            if table_name in metadata.tables:
                table = metadata.tables[table_name]
                session.execute(table.delete())
        session.commit()
    finally:
        session.close()


@pytest.fixture(scope="session")
def create_admin_user(app: Flask) -> None:
    with app.app_context():
        session = db_session_module.get_session()

        result = session.execute(
            text("SELECT id FROM usuarios WHERE email = :email"),
            {"email": TEST_ADMIN_EMAIL},
        )
        if result.fetchone():
            return

        hashed_password = bcrypt.hashpw(
            TEST_ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        )

        session.execute(
            text("""
                INSERT INTO enderecos (
                    logradouro, numero, bairro, cep, cidade, estado
                ) VALUES (
                    :logradouro, :numero, :bairro, :cep, :cidade, :estado
                )
            """),
            {
                "logradouro": "Rua Teste",
                "numero": "1",
                "bairro": "Centro",
                "cep": "30000-000",
                "cidade": "Belo Horizonte",
                "estado": "MG",
            },
        )

        endereco_result = session.execute(text("SELECT last_insert_rowid() as id"))
        endereco_row = endereco_result.fetchone()
        assert endereco_row is not None
        endereco_id = endereco_row[0]

        session.execute(
            text("""
                INSERT INTO usuarios (
                    nome, email, senha, urole, sexo, rg, cpf, profissao,
                    estado_civil, nascimento, celular, data_entrada,
                    bolsista, status, cert_atuacao_DAJ, criado, criadopor, endereco_id
                ) VALUES (
                    :nome, :email, :senha, :urole, :sexo, :rg, :cpf, :profissao,
                    :estado_civil, :nascimento, :celular, :data_entrada,
                    :bolsista, :status, :cert_atuacao_DAJ, :criado, :criadopor, :endereco_id
                )
            """),
            {
                "nome": "Admin Test",
                "email": TEST_ADMIN_EMAIL,
                "senha": hashed_password.decode("utf-8"),
                "urole": "admin",
                "sexo": "M",
                "rg": "123456789",
                "cpf": "123.456.789-00",
                "profissao": "Administrador",
                "estado_civil": "solteiro",
                "nascimento": "1990-01-01",
                "celular": "(11) 98765-4321",
                "data_entrada": "2024-01-01",
                "bolsista": False,
                "status": True,
                "cert_atuacao_DAJ": "sim",
                "criado": datetime.now(),
                "criadopor": 1,
                "endereco_id": endereco_id,
            },
        )
        session.commit()


@pytest.fixture
def auth_headers(client: FlaskClient, create_admin_user: None) -> dict[str, str]:
    login_response = client.post(
        "/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )

    assert login_response.status_code == 200, (
        f"Login failed with status {login_response.status_code}"
    )

    data = login_response.json
    assert data is not None, "Login response has no JSON data"
    assert "token" in data, f"Login response missing token: {data}"

    token = data["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_atendido_data() -> dict[str, Any]:
    return {
        "nome": "João Silva Teste",
        "data_nascimento": "1990-01-15",
        "cpf": "123.456.789-00",
        "telefone": "(11) 3333-4444",
        "celular": "(11) 98765-4321",
        "email": "joao.teste@exemplo.com",
        "estado_civil": "solteiro",
        "logradouro": "Rua Teste",
        "numero": "123",
        "bairro": "Centro",
        "cep": "12345-678",
        "cidade": "Belo Horizonte",
        "estado": "MG",
        "como_conheceu": "assist",
        "procurou_outro_local": "nao",
        "pj_constituida": "nao",
        "status": 1,
    }


@pytest.fixture
def sample_assistido_data() -> dict[str, Any]:
    return {
        "sexo": "M",
        "profissao": "Engenheiro",
        "raca": "parda",
        "rg": "12.345.678",
        "grau_instrucao": "superior_comp",
        "salario": 2000.0,
        "beneficio": "nao",
        "contribui_inss": "sim",
        "qtd_pessoas_moradia": 4,
        "renda_familiar": 5000.0,
        "participacao_renda": "principal",
        "tipo_moradia": "propria_quitada",
        "possui_outros_imoveis": False,
        "possui_veiculos": False,
        "doenca_grave_familia": "nao",
    }


@pytest.fixture
def sample_caso_data() -> dict[str, Any]:
    return {
        "id_usuario_responsavel": 1,
        "area_direito": "penal",
        "situacao_deferimento": "deferido",
        "ids_clientes": [],
    }

@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    return {
        "email": "test.user@gl.com",
        "nome": "Test User",
        "urole": "estag_direito",
        "sexo": "F",
        "rg": "98.765.432-1",
        "cpf": "987.654.321-00",
        "profissao": "Estagiário",
        "estado_civil": "solteiro",
        "nascimento": "1995-05-15",
        "telefone": "(11) 3333-4444",
        "celular": "(11) 99876-5432",
        "oab": None,
        "obs": None,
        "data_entrada": "2024-01-15",
        "data_saida": None,
        "matricula": "EST001",
        "bolsista": True,
        "tipo_bolsa": "integral",
        "horario_atendimento": "08:00-12:00",
        "suplente": None,
        "ferias": None,
        "cert_atuacao_DAJ": "sim",
        "inicio_bolsa": "2024-01-15T00:00:00",
        "fim_bolsa": None,
        "logradouro": "Rua Teste User",
        "numero": "456",
        "bairro": "Centro",
        "cep": "30000-111",
        "cidade": "Belo Horizonte",
        "estado": "MG",
        "complemento": None,
    }