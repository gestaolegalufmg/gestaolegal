from datetime import date, datetime

import bcrypt
import pytest
from sqlalchemy import create_engine, event, select

from scripts.seed_database import main, metadata, seed_database


@pytest.fixture
def engine():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def foreign_keys(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(metadata.tables["unidades"].insert(), [
            {"id": 7, "nome": "Belo Horizonte", "sigla": "BH", "ativa": True, "criado": datetime.now()},
            {"id": 12, "nome": "Nova Lima", "sigla": "NL", "ativa": True, "criado": datetime.now()},
            {"id": 15, "nome": "Inativa", "sigla": "OFF", "ativa": False, "criado": datetime.now()},
        ])
    yield engine
    engine.dispose()


def snapshot(engine):
    with engine.connect() as conn:
        return {t.name: conn.execute(select(t)).all() for t in metadata.sorted_tables}


def test_seed_relacoes_senha_e_idempotencia(engine):
    criados = seed_database(engine, senha="123456", hoje=date(2026, 10, 13))
    assert criados["usuarios"] == 4
    assert criados["atendidos"] == 40
    assert criados["assistidos"] == 20
    assert criados["casos"] == 4
    assert criados["eventos"] == 8
    with engine.connect() as conn:
        usuarios = metadata.tables["usuarios"]
        contas = conn.execute(select(usuarios)).mappings().all()
        assert {u["email"]: u["urole"] for u in contas} == {
            "admin@ufmg.br": "admin",
            "orient@ufmg.br": "orient",
            "estag_direito@ufmg.br": "estag_direito",
            "colab_ext@ufmg.br": "colab_ext",
        }
        for usuario in contas:
            assert bcrypt.checkpw(b"123456", usuario["senha"].encode())
        casos = metadata.tables["casos"]
        vinculos = metadata.tables["usuarios_unidades"]
        for caso in conn.execute(select(casos)).mappings():
            assert caso["unidade_id"] in (7, 12)
            assert conn.execute(select(vinculos).filter_by(
                usuario_id=caso["id_usuario_responsavel"], unidade_id=caso["unidade_id"]
            )).first()
        clientes = metadata.tables["atendidos"]
        links = metadata.tables["casos_atendidos"]
        pares = conn.execute(select(casos.c.unidade_id, clientes.c.unidade_id).select_from(
            links.join(casos, casos.c.id == links.c.id_caso).join(clientes, clientes.c.id == links.c.id_atendido)
        )).all()
        assert len(pares) == 4
        assert all(a == b for a, b in pares)
    antes = snapshot(engine)
    assert not seed_database(engine, senha="OutraSenha123!", hoje=date(2027, 1, 1))
    assert snapshot(engine) == antes


def test_dry_run_e_filtro_unidade(engine):
    antes = snapshot(engine)
    assert seed_database(engine, senha="123456", dry_run=True)["casos"] == 4
    assert snapshot(engine) == antes
    assert seed_database(engine, senha="123456", sigla="NL")["casos"] == 2
    with engine.connect() as conn:
        assert set(conn.execute(select(metadata.tables["casos"].c.unidade_id)).scalars()) == {12}


def test_falha_desfaz_insercoes_parciais(engine):
    antes = snapshot(engine)

    @event.listens_for(engine, "before_cursor_execute")
    def falhar(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO eventos"):
            raise RuntimeError("Falha simulada após criar usuários, atendidos e casos")

    with pytest.raises(RuntimeError, match="Falha simulada"):
        seed_database(engine, senha="123456")
    assert snapshot(engine) == antes


def test_unidade_inexistente_nao_insere(engine):
    antes = snapshot(engine)
    with pytest.raises(ValueError, match="Nenhuma unidade"):
        seed_database(engine, senha="123456", sigla="OFF")
    assert snapshot(engine) == antes


def test_reexecucao_preserva_edicoes(engine):
    seed_database(engine, senha="123456")
    casos = metadata.tables["casos"]
    with engine.begin() as conn:
        conn.execute(casos.update().values(situacao_deferimento="arquivado", status=False))
    antes = snapshot(engine)
    seed_database(engine, senha="123456")
    assert snapshot(engine) == antes


def test_cli_bloqueia_producao(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_cpfs_validos_unicos_e_metade_assistidos_por_unidade(engine):
    seed_database(engine, senha="123456")
    cpfs = []
    with engine.connect() as conn:
        for table_name in ("usuarios", "atendidos"):
            for cpf in conn.execute(select(metadata.tables[table_name].c.cpf)).scalars():
                digits = [int(c) for c in cpf if c.isdigit()]
                assert len(digits) == 11 and len(set(digits)) > 1
                for length in (9, 10):
                    check = (sum(digits[i] * (length + 1 - i) for i in range(length)) * 10 % 11) % 10
                    assert digits[length] == check
                cpfs.append(cpf)
        assert len(cpfs) == len(set(cpfs)) == 44
        atendidos, assistidos = metadata.tables["atendidos"], metadata.tables["assistidos"]
        for unidade in (7, 12):
            people = set(conn.execute(select(atendidos.c.id).where(atendidos.c.unidade_id == unidade)).scalars())
            assisted = set(conn.execute(select(assistidos.c.id_atendido).where(assistidos.c.id_atendido.in_(people))).scalars())
            assert len(people) == 20
            assert len(assisted) == 10


def test_atualiza_rotulos_antigos_sem_duplicar_ou_alterar_vinculos(engine):
    from scripts.seed_database import MARCA, MARCA_ANTIGA

    seed_database(engine, senha="123456")
    esperado = snapshot(engine)
    with engine.begin() as conn:
        for table_name in ("usuarios", "atendidos"):
            tabela = metadata.tables[table_name]
            for row in conn.execute(select(tabela)).mappings().all():
                values = {"nome": row["nome"] + " Seed", "cpf": "000.000.000-00", "obs": MARCA_ANTIGA}
                if table_name == "usuarios":
                    values["rg"] = "SEED"
                else:
                    values["email"] = row["email"].replace("@example.test", "@seed.example.test")
                conn.execute(tabela.update().where(tabela.c.id == row["id"]).values(**values))
        for table_name, column in (("casos", "descricao"), ("processos", "identificacao"),
                                   ("eventos", "descricao"), ("lembretes", "descricao"),
                                   ("orientacao_juridica", "descricao"), ("plantao", "nome")):
            tabela = metadata.tables[table_name]
            for row in conn.execute(select(tabela)).mappings().all():
                conn.execute(tabela.update().where(tabela.c.id == row["id"]).values(
                    **{column: row[column].replace(MARCA, MARCA_ANTIGA)}))
    assert not seed_database(engine, senha="OutraSenha123!")
    assert snapshot(engine) == esperado
    for rows in esperado.values():
        for row in rows:
            assert all("seed" not in value.lower() for key, value in row._mapping.items()
                       if isinstance(value, str) and key != "senha")
