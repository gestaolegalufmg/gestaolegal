import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    COMPANY_NAME = os.environ.get("COMPANY_NAME", "Gestão Legal")
    COMPANY_COLOR = os.environ.get("COMPANY_COLOR", "#1758ac")

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")

    UPLOADS = "./static/casos"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB limit

    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = False

    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError(
            "All database environment variables (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME) are required"
        )

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}/{db}".format(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, db=DB_NAME
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 10}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_PADRAO = 10
    USUARIOS_POR_PAGINA = 20
    HISTORICOS_POR_PAGINA = 20
    ATENDIDOS_POR_PAGINA = 20
    ASSISTENCIA_JURIDICA_POR_PAGINA = 20
    CASOS_POR_PAGINA = 20
    ARQUIVOS_POR_PAGINA = 20
    EVENTOS_POR_PAGINA = 20

    FLASK_ENV = os.environ.get("FLASK_ENV")

    if FLASK_ENV == "development":
        MAIL_SERVER = "mailpit"
        MAIL_PORT = 1025
        MAIL_USE_SSL = False
        MAIL_USE_TLS = False
        MAIL_USERNAME = None
        MAIL_PASSWORD = None
        MAIL_DEFAULT_SENDER = "development@gestaolegal.com"
    else:
        MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
        MAIL_PORT = int(os.environ.get("MAIL_PORT", "465"))
        MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"
        MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
        MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
