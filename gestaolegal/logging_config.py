import logging
import os
from datetime import datetime


def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_filename = os.path.join(
        log_dir, f"gestaolegal_{datetime.now().strftime('%Y%m%d')}.log"
    )

    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    loggers = [
        "gestaolegal.services.atendido_service",
        "gestaolegal.services.assistencia_judiciaria_service",
        "gestaolegal.services.assistido_service",
        "gestaolegal.services.base_service",
        "gestaolegal.services.endereco_service",
        "gestaolegal.services.notificacao_service",
        "gestaolegal.services.orientacao_juridica_service",
        "gestaolegal.services.plantao_service",
        "gestaolegal.services.usuario_service",
        "gestaolegal.controllers.arquivo_controller",
        "gestaolegal.controllers.assistencia_judiciaria_controller",
        "gestaolegal.controllers.atendido_controller",
        "gestaolegal.controllers.casos_controller",
        "gestaolegal.controllers.notificacoes_controller",
        "gestaolegal.controllers.orientacao_juridica_controller",
        "gestaolegal.controllers.plantao_controller",
        "gestaolegal.controllers.principal_controller",
        "gestaolegal.controllers.relatorio_controller",
        "gestaolegal.controllers.user_controller",
        "gestaolegal",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("flask").setLevel(logging.WARNING)
