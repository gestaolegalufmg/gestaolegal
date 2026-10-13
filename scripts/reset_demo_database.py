"""Apaga e recria exclusivamente o banco confirmado por DEMO_DB_NAME.

Use scripts/reset_demo.sh para também parar a API durante a operação.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.seed_database import seed_database
SYSTEM_DATABASES = {"mysql", "sys", "information_schema", "performance_schema"}


def configuration():
    load_dotenv(ROOT / ".env")
    if os.environ.get("FLASK_ENV", "development") not in {"development", "testing"}:
        raise ValueError("Reset disponível apenas com FLASK_ENV=development ou testing.")
    for key in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME", "DEMO_DB_NAME"):
        if not os.environ.get(key):
            raise ValueError(f"Configure {key} no ambiente ou .env.")
    name = os.environ["DB_NAME"]
    if name != os.environ["DEMO_DB_NAME"] or name.lower() in SYSTEM_DATABASES:
        raise ValueError("DEMO_DB_NAME deve confirmar exatamente DB_NAME, fora dos bancos de sistema.")
    password = os.environ.get("SEED_PASSWORD", "123456")
    if not 6 <= len(password.encode("utf-8")) <= 72:
        raise ValueError("SEED_PASSWORD deve ter entre 6 e 72 bytes em UTF-8.")
    url = URL.create("mysql+pymysql", username=os.environ["DB_USER"],
                     password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"],
                     port=int(os.environ.get("DB_PORT", "3306")), database=name)
    config = Config(str(ROOT / "migrations/alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.attributes["database_url"] = url
    # Detecta migrations ausentes ou heads divergentes antes de apagar dados.
    if ScriptDirectory.from_config(config).get_current_head() is None:
        raise ValueError("Nenhuma migration encontrada.")
    return url, password, config


def reset(url, password, config):
    server = create_engine(url.set(database=None), isolation_level="AUTOCOMMIT")
    try:
        with server.connect() as conn:
            # O lock vive nesta conexão, inclusive durante migrations e seed.
            lock = "demo-reset:" + hashlib.sha256(url.database.encode()).hexdigest()[:48]
            if conn.execute(text("SELECT GET_LOCK(:name, 0)"), {"name": lock}).scalar() != 1:
                raise ValueError("Outro reset deste banco já está em execução.")
            try:
                name = server.dialect.identifier_preparer.quote_identifier(url.database)
                print(f"Recriando banco {name}...", flush=True)
                conn.exec_driver_sql(f"DROP DATABASE IF EXISTS {name}")
                conn.exec_driver_sql(f"CREATE DATABASE {name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                command.upgrade(config, "head")
                engine = create_engine(url)
                try:
                    seed_database(engine, senha=password)
                finally:
                    engine.dispose()
                print("Reset de demonstração concluído.", flush=True)
            finally:
                conn.execute(text("SELECT RELEASE_LOCK(:name)"), {"name": lock})
    finally:
        server.dispose()


def main():
    try:
        settings = configuration()
        if sys.argv[1:] == ["--check"]:
            print("Configuração do reset validada.")
        elif sys.argv[1:]:
            raise ValueError("Uso: reset_demo_database.py [--check]")
        else:
            reset(*settings)
    except ValueError as exc:
        print(f"reset-demo: {exc}", file=sys.stderr)
        return 1
    except Exception:
        # Exceções SQL podem conter credenciais ou parâmetros privados.
        print("reset-demo: falha ao recriar o banco, aplicar migrations ou executar seed. "
              "O reset não é transacional; corrija a causa e execute novamente.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
