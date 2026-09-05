import os
from urllib.parse import unquote

from flask import Flask, abort, request
from flask_cors import CORS
from flask_mail import Mail

from gestaolegal.utils.json_encoder import CustomJSONEncoder

mail = Mail()


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False

    if config_object:
        app.config.from_object(config_object)
    else:
        configure_app(app)

    app.json_provider_class = CustomJSONEncoder

    from gestaolegal.logging_config import setup_logging

    setup_logging()

    initialize_extensions(app)

    from gestaolegal.handlers import register_handlers

    register_handlers(app)

    register_blueprints(app)

    register_static_block(app)

    from gestaolegal.utils.error_handlers import register_error_handlers

    register_error_handlers(app)

    return app


# Categorias de anexo que já viveram sob `gestaolegal/static/` (#190). O Flask
# serve `app.static_folder` em `/static/<path>` sem autenticação, então o caminho
# estático continua bloqueado mesmo depois da mudança para o volume privado.
BLOCKED_STATIC_PREFIXES = ("casos", "eventos", "arquivos")


def _partes_normalizadas(caminho: str) -> list[str]:
    """Resolve '.', '..' e segmentos vazios ('//') do caminho de uma requisição."""
    partes: list[str] = []
    for segmento in caminho.split("/"):
        if segmento in ("", "."):
            continue
        if segmento == "..":
            if partes:
                partes.pop()
            continue
        partes.append(segmento)
    return partes


def _e_caminho_de_anexo_estatico(caminho: str) -> bool:
    partes = _partes_normalizadas(caminho)
    return (
        len(partes) >= 2
        and partes[0] == "static"
        and partes[1] in BLOCKED_STATIC_PREFIXES
    )


def register_static_block(app):
    """Devolve 404 em /static/casos, /static/eventos e /static/arquivos (#190).

    Os anexos passaram para o volume privado, mas o diretório estático pode
    continuar existindo em instalações antigas (e nas imagens já construídas).
    Enquanto `/static/<path>` for servido sem autenticação, esses três prefixos
    precisam responder 404, inclusive nas formas com '//', '%2e%2e' e barra
    final. O restante de `static/` — `imgs_daj`, por exemplo — segue público.
    """

    @app.before_request
    def bloqueia_anexos_estaticos():
        caminhos = {request.path, unquote(request.path)}
        raw = request.environ.get("RAW_URI") or request.environ.get("REQUEST_URI")
        if raw:
            caminho_raw = raw.split("?", 1)[0]
            caminhos.add(caminho_raw)
            caminhos.add(unquote(caminho_raw))
        if any(_e_caminho_de_anexo_estatico(c) for c in caminhos):
            abort(404)


def configure_app(app):
    from gestaolegal.config import Config

    app.config.from_object(Config)
    validate_private_files_root(app)


def _esta_dentro(caminho: str, possivel_pai: str) -> bool:
    try:
        return os.path.commonpath([caminho, possivel_pai]) == possivel_pai
    except ValueError:  # drives/roots diferentes
        return False


def validate_private_files_root(app):
    """Falha a subida se a raiz privada dos anexos não servir (#190).

    O Flask serve `app.static_folder` em `/static/<path>` sem autenticação, então
    uma raiz de anexos dentro dela (ou contendo ela) expõe arquivo de atendido.
    A raiz também precisa existir e ser gravável — descobrir isso no primeiro
    upload significa descobrir tarde demais.
    """
    root = app.config.get("PRIVATE_FILES_ROOT")
    if not root:
        raise RuntimeError(
            "PRIVATE_FILES_ROOT não configurado: defina a raiz privada dos anexos."
        )

    real_root = os.path.realpath(root)

    static_folder = app.static_folder
    if static_folder:
        real_static = os.path.realpath(static_folder)
        if _esta_dentro(real_root, real_static) or _esta_dentro(real_static, real_root):
            raise RuntimeError(
                f"PRIVATE_FILES_ROOT ({real_root}) não pode se sobrepor à pasta "
                f"estática servida pelo Flask ({real_static}): os anexos ficariam "
                "acessíveis em /static sem autenticação."
            )

    try:
        os.makedirs(real_root, exist_ok=True)
    except OSError as e:
        raise RuntimeError(
            f"PRIVATE_FILES_ROOT ({real_root}) não pôde ser criado: {e}"
        ) from e

    if not os.path.isdir(real_root) or not os.access(real_root, os.W_OK | os.X_OK):
        raise RuntimeError(
            f"PRIVATE_FILES_ROOT ({real_root}) não é um diretório gravável."
        )

    app.config["PRIVATE_FILES_ROOT"] = real_root


def initialize_extensions(app):
    from gestaolegal.config import Config

    mail.init_app(app)
    cors_kwargs = {"supports_credentials": True}
    if Config.CORS_ORIGINS:
        cors_kwargs["origins"] = Config.CORS_ORIGINS
    CORS(app, resources={r"/*": cors_kwargs})


def register_blueprints(app):
    from gestaolegal.controllers import routes

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
