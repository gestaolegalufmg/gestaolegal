from dataclasses import dataclass


@dataclass
class Roteiro:
    area_direito: str
    link: str | None = None
    id: int | None = None
