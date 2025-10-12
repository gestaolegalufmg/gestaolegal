from dataclasses import dataclass


@dataclass
class ArquivoCaso:
    id_caso: int
    link_arquivo: str

    id: int | None = None
