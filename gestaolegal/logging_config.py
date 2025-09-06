import logging
import os
from datetime import datetime


def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    log_filename = os.path.join(
        log_dir, f"gestaolegal_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # Configure logging format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure console handler with DEBUG level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Configure file handler
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Set specific loggers to DEBUG level
    loggers = [
        "gestaolegal.services.atendido_service",
        "gestaolegal.controllers.plantao_controller",
        "gestaolegal.controllers.atendido_controller",
        "gestaolegal",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # Ensure logs propagate to root logger

    # Reduce noise from third-party libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("flask").setLevel(logging.WARNING)
