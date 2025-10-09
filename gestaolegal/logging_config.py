import logging
import os


class LastPartFilter(logging.Filter):
    def filter(self, record):
        record.name_last = record.name.rsplit(".", 1)[-1]
        return True


def setup_logging():
    log_format = (
        "[%(levelname)s] [%(asctime)s] [%(name_last)s@%(funcName)s]: %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()

    console_handler = logging.StreamHandler()

    env = os.environ.get("FLASK_ENV", "production")
    console_handler.setLevel(logging.DEBUG if env == "development" else logging.INFO)

    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    console_handler.addFilter(LastPartFilter())

    root_logger.setLevel(logging.DEBUG if env == "development" else logging.INFO)
    root_logger.addHandler(console_handler)
