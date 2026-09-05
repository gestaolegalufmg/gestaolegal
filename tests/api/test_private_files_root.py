"""Validação da raiz privada dos anexos na subida do app (#190)."""

import os

import pytest
from flask import Flask

from gestaolegal import validate_private_files_root


def _app(root: str) -> Flask:
    app = Flask(__name__)
    app.config["PRIVATE_FILES_ROOT"] = root
    return app


def test_raiz_valida_e_normalizada(tmp_path):
    root = tmp_path / "uploads"
    app = _app(str(root))

    validate_private_files_root(app)

    assert root.is_dir()
    assert app.config["PRIVATE_FILES_ROOT"] == os.path.realpath(str(root))


def test_recusa_raiz_dentro_da_pasta_estatica(tmp_path):
    app = _app("")
    static = tmp_path / "static"
    (static / "casos").mkdir(parents=True)
    app.static_folder = str(static)
    app.config["PRIVATE_FILES_ROOT"] = str(static / "casos")

    with pytest.raises(RuntimeError, match="pasta estática"):
        validate_private_files_root(app)


def test_recusa_raiz_que_contem_a_pasta_estatica(tmp_path):
    app = _app(str(tmp_path))
    static = tmp_path / "static"
    static.mkdir()
    app.static_folder = str(static)

    with pytest.raises(RuntimeError, match="pasta estática"):
        validate_private_files_root(app)


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root ignora permissão de escrita",
)
def test_recusa_raiz_nao_gravavel(tmp_path):
    pai = tmp_path / "somente-leitura"
    pai.mkdir()
    root = pai / "uploads"
    root.mkdir()
    os.chmod(root, 0o500)
    try:
        app = _app(str(root))
        with pytest.raises(RuntimeError, match="gravável"):
            validate_private_files_root(app)
    finally:
        os.chmod(root, 0o700)


def test_recusa_raiz_nao_configurada():
    app = _app("")

    with pytest.raises(RuntimeError, match="PRIVATE_FILES_ROOT não configurado"):
        validate_private_files_root(app)
