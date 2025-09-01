from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.usuario import Usuario
    from gestaolegal.schemas.processo import ProcessoSchema


@dataclass(frozen=True)
class Processo:
    id: int
    especie: str
    numero: int | None
    identificacao: str | None
    vara: str | None
    link: str | None
    probabilidade: str | None
    posicao_assistido: str | None
    valor_causa_inicial: int | None
    valor_causa_atual: int | None
    data_distribuicao: date | None
    data_transito_em_julgado: date | None
    obs: str | None
    id_caso: int
    caso: "Caso"
    status: bool
    id_criado_por: int
    criado_por: "Usuario"

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(processo: "ProcessoSchema") -> "Processo":
        return Processo(
            id=processo.id,
            especie=processo.especie,
            numero=processo.numero,
            identificacao=processo.identificacao,
            vara=processo.vara,
            link=processo.link,
            probabilidade=processo.probabilidade,
            posicao_assistido=processo.posicao_assistido,
            valor_causa_inicial=processo.valor_causa_inicial,
            valor_causa_atual=processo.valor_causa_atual,
            data_distribuicao=processo.data_distribuicao,
            data_transito_em_julgado=processo.data_transito_em_julgado,
            obs=processo.obs,
            id_caso=processo.id_caso,
            caso=processo.caso,
            status=processo.status,
            id_criado_por=processo.id_criado_por,
            criado_por=processo.criado_por,
        )
