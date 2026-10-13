from unittest.mock import MagicMock

import pytest
from sqlalchemy.engine import URL

from scripts import reset_demo_database as resetter


@pytest.fixture
def demo_env(monkeypatch):
    monkeypatch.setattr(resetter, "load_dotenv", lambda *_: None)
    for key, value in {
        "FLASK_ENV": "testing", "DB_USER": "demo", "DB_PASSWORD": "p@ss%word",
        "DB_HOST": "db", "DB_PORT": "3307", "DB_NAME": "demo",
        "DEMO_DB_NAME": "demo", "SEED_PASSWORD": "123456",
    }.items():
        monkeypatch.setenv(key, value)


def test_configuration(demo_env):
    url, password, config = resetter.configuration()
    assert url.database == "demo"
    assert url.port == 3307
    assert url.password == "p@ss%word"
    assert password == "123456"
    assert config.attributes["database_url"] == url


@pytest.mark.parametrize("key,value", [
    ("FLASK_ENV", "production"), ("FLASK_ENV", "demo"),
    ("DEMO_DB_NAME", "other"), ("DEMO_DB_NAME", ""),
    ("DB_PASSWORD", ""), ("SEED_PASSWORD", "12345"),
    ("SEED_PASSWORD", "x" * 73),
])
def test_rejects_invalid_configuration(demo_env, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError):
        resetter.configuration()


@pytest.mark.parametrize("name", resetter.SYSTEM_DATABASES)
def test_rejects_system_database(demo_env, monkeypatch, name):
    monkeypatch.setenv("DB_NAME", name)
    monkeypatch.setenv("DEMO_DB_NAME", name)
    with pytest.raises(ValueError):
        resetter.configuration()


@pytest.fixture
def operations(monkeypatch):
    server, engine = MagicMock(), MagicMock()
    conn = server.connect.return_value.__enter__.return_value
    conn.execute.return_value.scalar.return_value = 1
    server.dialect.identifier_preparer.quote_identifier.side_effect = lambda n: f"`{n}`"
    factory = MagicMock(side_effect=[server, engine])
    monkeypatch.setattr(resetter, "create_engine", factory)
    upgrade, seed = MagicMock(), MagicMock()
    monkeypatch.setattr(resetter.command, "upgrade", upgrade)
    monkeypatch.setattr(resetter, "seed_database", seed)
    steps = MagicMock()
    steps.attach_mock(conn.exec_driver_sql, "ddl")
    steps.attach_mock(upgrade, "migrate")
    steps.attach_mock(seed, "seed")
    return server, engine, conn, upgrade, seed, steps


def test_reset_order_and_cleanup(operations):
    server, engine, conn, upgrade, seed, steps = operations
    url = URL.create("mysql+pymysql", database="demo")
    config = object()
    resetter.reset(url, "123456", config)
    assert [c[0] for c in steps.mock_calls] == ["ddl", "ddl", "migrate", "seed"]
    assert conn.exec_driver_sql.call_args_list[0].args == ("DROP DATABASE IF EXISTS `demo`",)
    upgrade.assert_called_once_with(config, "head")
    seed.assert_called_once_with(engine, senha="123456")
    assert "RELEASE_LOCK" in str(conn.execute.call_args.args[0])
    engine.dispose.assert_called_once()
    server.dispose.assert_called_once()


def test_busy_lock_does_not_drop(operations):
    server, _, conn, upgrade, seed, _ = operations
    conn.execute.return_value.scalar.return_value = 0
    with pytest.raises(ValueError, match="Outro reset"):
        resetter.reset(URL.create("mysql+pymysql", database="demo"), "123456", object())
    conn.exec_driver_sql.assert_not_called()
    upgrade.assert_not_called()
    seed.assert_not_called()
    server.dispose.assert_called_once()


def test_migration_failure_stops_before_seed(operations):
    server, _, conn, upgrade, seed, _ = operations
    upgrade.side_effect = RuntimeError("migration falhou")
    with pytest.raises(RuntimeError):
        resetter.reset(URL.create("mysql+pymysql", database="demo"), "123456", object())
    seed.assert_not_called()
    assert "RELEASE_LOCK" in str(conn.execute.call_args.args[0])
    server.dispose.assert_called_once()


@pytest.mark.parametrize("fail_at,expected", [
    ("", ["check", "stop", "reset", "start"]),
    ("check", ["check"]),
    ("stop", ["check", "stop"]),
    ("reset", ["check", "stop", "reset"]),
])
def test_wrapper_sequence(tmp_path, monkeypatch, fail_at, expected):
    import os
    import shutil
    import subprocess

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy(resetter.ROOT / "scripts/reset_demo.sh", scripts)
    binary = tmp_path / "docker"
    binary.write_text('''#!/usr/bin/env bash
set -eu
case "$*" in
  *--check) step=check ;;
  *" stop "*) step=stop ;;
  *" start "*) step=start ;;
  *) step=reset ;;
esac
printf '%s\\n' "$step" >> "$TEST_LOG"
if [ "$step" = "$FAIL_AT" ]; then exit 1; fi
''')
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    monkeypatch.setenv("TEST_LOG", str(tmp_path / "calls"))
    monkeypatch.setenv("FAIL_AT", fail_at)
    result = subprocess.run(["bash", str(scripts / "reset_demo.sh")], cwd="/tmp",
                            capture_output=True, text=True)
    assert (result.returncode == 0) == (not fail_at), result.stderr
    assert (tmp_path / "calls").read_text().splitlines() == expected
