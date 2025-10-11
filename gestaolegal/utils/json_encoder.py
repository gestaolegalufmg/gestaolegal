import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime

from flask.json.provider import DefaultJSONProvider

logger = logging.getLogger(__name__)


class CustomJSONEncoder(DefaultJSONProvider):
    @staticmethod
    def default(o: object):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif is_dataclass(o) and not isinstance(o, type):
            return asdict(o)

        return DefaultJSONProvider.default(o)
