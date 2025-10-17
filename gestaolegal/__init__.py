from flask import Flask
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

    return app


def configure_app(app):
    from gestaolegal.config import Config

    app.config.from_object(Config)


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
