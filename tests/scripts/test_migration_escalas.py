"""Preservação dos registros anteriores e proteção de downgrade."""

import importlib
from datetime import date, datetime

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def test_migration_preserva_legado_e_vincula_por_unidade():
    engine = sa.create_engine("sqlite://")
    meta = sa.MetaData()
    p = sa.Table(
        "plantao",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("unidade_id", sa.Integer),
        sa.Column("data_abertura", sa.DateTime),
        sa.Column("data_fechamento", sa.DateTime),
    )
    d = sa.Table(
        "dias_plantao",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("unidade_id", sa.Integer),
        sa.Column("data", sa.Date),
        sa.Column("status", sa.Boolean),
    )
    m = sa.Table(
        "dias_marcados_plantao",
        meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("unidade_id", sa.Integer),
        sa.Column("data_marcada", sa.Date),
        sa.Column("status", sa.Boolean),
        sa.Column("confirmacao", sa.String(15)),
        sa.Column("id_usuario", sa.Integer),
    )
    meta.create_all(engine)
    migration = importlib.import_module(
        "migrations.versions.d1e2f3a4b5c6_escalas_plantao"
    )
    with engine.begin() as conn:
        conn.execute(
            p.insert(),
            [
                {"id": 1, "unidade_id": 1, "data_abertura": datetime(2025, 1, 1)},
                {"id": 2, "unidade_id": 1, "data_abertura": None},
            ],
        )
        conn.execute(
            d.insert(),
            [
                {"id": 1, "unidade_id": 1, "data": date(2025, 1, 2), "status": False},
                {"id": 2, "unidade_id": 2, "data": None, "status": True},
            ],
        )
        conn.execute(
            m.insert(),
            [
                {
                    "id": 1,
                    "unidade_id": 1,
                    "data_marcada": date(2025, 1, 2),
                    "status": False,
                    "confirmacao": "confirmar",
                    "id_usuario": 4,
                },
                {
                    "id": 2,
                    "unidade_id": 2,
                    "data_marcada": None,
                    "status": True,
                    "confirmacao": "aberto",
                    "id_usuario": None,
                },
            ],
        )
        before = {
            t.name: [dict(r) for r in conn.execute(sa.select(t)).mappings()]
            for t in (p, d, m)
        }
        with Operations.context(MigrationContext.configure(conn)):
            migration.upgrade()
        tables = {n: sa.Table(n, sa.MetaData(), autoload_with=conn) for n in before}
        after = {
            n: [dict(r) for r in conn.execute(sa.select(t)).mappings()]
            for n, t in tables.items()
        }
        for name in before:
            for row in before[name]:
                migrated = next(r for r in after[name] if r["id"] == row["id"])
                assert all(migrated[k] == v for k, v in row.items())
        scales = {r["id"]: r for r in after["plantao"]}
        assert all(r["legado"] for r in scales.values())
        for name in ("dias_plantao", "dias_marcados_plantao"):
            assert all(
                scales[r["plantao_id"]]["unidade_id"] == r["unidade_id"]
                for r in after[name]
            )
            assert not next(
                c
                for c in sa.inspect(conn).get_columns(name)
                if c["name"] == "plantao_id"
            )["nullable"]
        conn.execute(
            tables["plantao"].insert().values(unidade_id=1, nome="Nova", legado=False)
        )
        with (
            Operations.context(MigrationContext.configure(conn)),
            pytest.raises(RuntimeError, match="Downgrade"),
        ):
            migration.downgrade()
