import os
import secrets
import warnings
from typing import ClassVar, Literal, TypedDict, final

from dotenv import load_dotenv

load_dotenv()

Environment = Literal["development", "production", "testing"]


class _MailConfig(TypedDict):
    server: str
    port: int
    use_ssl: bool
    use_tls: bool
    username: str | None
    password: str | None
    default_sender: str


def _get_flask_env() -> Environment:
    env = os.environ.get("FLASK_ENV", "development")
    if env not in ("development", "production", "testing"):
        warnings.warn(
            f"Invalid FLASK_ENV '{env}', defaulting to 'development'",
            UserWarning,
            stacklevel=2,
        )
        return "development"
    return env


def _get_or_generate_jwt_secret_key(env: Environment) -> str:
    jwt_secret_key = os.environ.get("JWT_SECRET_KEY")

    if not jwt_secret_key:
        if env == "production":
            raise ValueError(
                "JWT_SECRET_KEY is required in production! " + \
                "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
            )

        generated_key = secrets.token_hex(32)
        warnings.warn(
            "No JWT_SECRET_KEY set - using auto-generated key for development. " + \
            "This key will change on restart, logging out all users.",
            UserWarning,
            stacklevel=2,
        )
        return generated_key

    if env == "production" and len(jwt_secret_key) < 32:
        raise ValueError(
            f"JWT_SECRET_KEY too short for production ({len(jwt_secret_key)} chars). " + \
            "Use at least 32 characters. " + \
            "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
        )

    return jwt_secret_key


def _get_required_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"{key} environment variable is required")
    return value


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if not value:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _get_mail_config(env: Environment) -> _MailConfig:
    if env == "development":
        return _MailConfig(
            server="mailpit",
            port=1025,
            use_ssl=False,
            use_tls=False,
            username=None,
            password=None,
            default_sender="development@gestaolegal.com",
        )
    else:
        return _MailConfig(
            server=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
            port=int(os.environ.get("MAIL_PORT", "465")),
            use_ssl=_parse_bool(os.environ.get("MAIL_USE_SSL"), default=True),
            use_tls=_parse_bool(os.environ.get("MAIL_USE_TLS"), default=False),
            username=os.environ.get("MAIL_USERNAME"),
            password=os.environ.get("MAIL_PASSWORD"),
            default_sender=os.environ.get(
                "MAIL_DEFAULT_SENDER", "noreply@gestaolegal.com"
            ),
        )


@final
class Config:
    FLASK_ENV: ClassVar[Environment] = _get_flask_env()
    COMPANY_NAME: ClassVar[str] = os.environ.get("COMPANY_NAME", "Gestão Legal")
    JWT_SECRET_KEY: ClassVar[str] = _get_or_generate_jwt_secret_key(FLASK_ENV)
    STATIC_ROOT_DIR: ClassVar[str] = os.environ.get(
        "STATIC_ROOT_DIR", "/gestaolegal/gestaolegal/static/"
    )
    UPLOADS: ClassVar[str] = os.path.join(STATIC_ROOT_DIR, "casos")
    MAX_CONTENT_LENGTH: ClassVar[int] = 10 * 1024 * 1024  # 10 MB

    DB_USER: ClassVar[str] = _get_required_env("DB_USER")
    DB_PASSWORD: ClassVar[str] = _get_required_env("DB_PASSWORD")
    DB_HOST: ClassVar[str] = _get_required_env("DB_HOST")
    DB_NAME: ClassVar[str] = _get_required_env("DB_NAME")

    SQLALCHEMY_DATABASE_URI: ClassVar[str] = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict[str, int]] = {"pool_recycle": 10}
    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = False

    ADMIN_PADRAO: ClassVar[int] = 10
    USUARIOS_POR_PAGINA: ClassVar[int] = 20
    HISTORICOS_POR_PAGINA: ClassVar[int] = 20
    ATENDIDOS_POR_PAGINA: ClassVar[int] = 20
    CASOS_POR_PAGINA: ClassVar[int] = 20
    ARQUIVOS_POR_PAGINA: ClassVar[int] = 20
    EVENTOS_POR_PAGINA: ClassVar[int] = 20

    _mail_config: ClassVar[_MailConfig] = _get_mail_config(FLASK_ENV)

    MAIL_SERVER: ClassVar[str] = _mail_config["server"]
    MAIL_PORT: ClassVar[int] = _mail_config["port"]
    MAIL_USE_SSL: ClassVar[bool] = _mail_config["use_ssl"]
    MAIL_USE_TLS: ClassVar[bool] = _mail_config["use_tls"]
    MAIL_USERNAME: ClassVar[str | None] = _mail_config["username"]
    MAIL_PASSWORD: ClassVar[str | None] = _mail_config["password"]
    MAIL_DEFAULT_SENDER: ClassVar[str] = _mail_config["default_sender"]
