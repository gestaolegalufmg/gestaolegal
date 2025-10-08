from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail

from gestaolegal.utils.json_encoder import CustomJSONEncoder

bcrypt = Bcrypt()
mail = Mail()


def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    if config_object:
        app.config.from_object(config_object)
    else:
        configure_app(app)

    # Set custom JSON encoder for ISO date format
    app.json_default_provider_class = CustomJSONEncoder
    app.json = CustomJSONEncoder(app)

    # Initialize logging
    from gestaolegal.logging_config import setup_logging

    setup_logging()

    initialize_extensions(app)

    register_blueprints(app)

    return app


def configure_app(app):
    from gestaolegal.config import Config

    app.config.from_object(Config)


def initialize_extensions(app):
    bcrypt.init_app(app)
    mail.init_app(app)
    CORS(app)

    from gestaolegal.middleware import ReverseProxied

    app.wsgi_app = ReverseProxied(app.wsgi_app)


def register_blueprints(app):
    from gestaolegal.controllers import routes

    for route, url_prefix in routes:
        app.register_blueprint(route, url_prefix=url_prefix)
