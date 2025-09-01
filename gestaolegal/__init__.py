from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from gestaolegal.utils.formatters import (
    formatarNomeDoUsuario,
    formatarSituacaoDeferimento,
    formatarTipoDeEvento,
)

bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_object:
        app.config.from_object(config_object)
    else:
        configure_app(app)

    initialize_extensions(app)

    register_blueprints(app)

    register_context_processors(app)

    register_error_handlers(app)

    app.jinja_env.globals.update(formatarTipoDeEvento=formatarTipoDeEvento)
    app.jinja_env.globals.update(
        formatarNomeDoUsuario=lambda id_usuario, db: formatarNomeDoUsuario(
            id_usuario, db
        )
    )
    app.jinja_env.globals.update(
        formatarSituacaoDeferimento=formatarSituacaoDeferimento
    )

    return app


def configure_app(app):
    from gestaolegal.config import Config

    app.config.from_object(Config)


def initialize_extensions(app):
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "usuario.login"
    login_manager.login_message = "Por favor, faça o login para acessar esta página."

    from gestaolegal.middleware import ReverseProxied

    app.wsgi_app = ReverseProxied(app.wsgi_app)

    from gestaolegal import database

    database.init_app(app)


def register_blueprints(app):
    from gestaolegal.controllers import routes

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)


def register_context_processors(app):
    from gestaolegal.utils.context_processors import (
        inject_company_config,
        insere_area_atuacao,
        insere_assistencia_jud_areas_atendidas,
        insere_assistencia_jud_regioes,
        insere_beneficio,
        insere_como_conheceu_dajUsuario,
        insere_contribuicao_inss,
        insere_enquadramento,
        insere_escolaridade,
        insere_estado_civilUsuario,
        insere_moradia,
        insere_orgao_reg,
        insere_participacao_renda,
        insere_qual_pessoa_doente,
        insere_regiao_bh,
        insere_sexo_usuario,
        insere_situacao_deferimento,
        insere_tipo_bolsaUsuario,
        insere_tipo_evento,
        insere_usuario_roles,
        processor_formata_float,
        processor_tipo_classe,
    )

    app.context_processor(inject_company_config)
    app.context_processor(processor_tipo_classe)
    app.context_processor(processor_formata_float)
    app.context_processor(insere_usuario_roles)
    app.context_processor(insere_tipo_bolsaUsuario)
    app.context_processor(insere_sexo_usuario)
    app.context_processor(insere_estado_civilUsuario)
    app.context_processor(insere_como_conheceu_dajUsuario)
    app.context_processor(insere_assistencia_jud_areas_atendidas)
    app.context_processor(insere_assistencia_jud_regioes)
    app.context_processor(insere_beneficio)
    app.context_processor(insere_contribuicao_inss)
    app.context_processor(insere_participacao_renda)
    app.context_processor(insere_moradia)
    app.context_processor(insere_qual_pessoa_doente)
    app.context_processor(insere_regiao_bh)
    app.context_processor(insere_escolaridade)
    app.context_processor(insere_enquadramento)
    app.context_processor(insere_area_atuacao)
    app.context_processor(insere_orgao_reg)
    app.context_processor(insere_situacao_deferimento)
    app.context_processor(insere_tipo_evento)


def register_error_handlers(app):
    from gestaolegal.utils.error_handlers import (
        error_403,
        error_404,
        error_413,
        error_500,
    )

    app.register_error_handler(404, error_404)
    app.register_error_handler(403, error_403)
    app.register_error_handler(413, error_413)
    app.register_error_handler(500, error_500)
