from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.atendido import Atendido
    from gestaolegal.models.usuario import Usuario
    from gestaolegal.schemas.caso import Caso as CasoSchema


@dataclass(frozen=True)
class Caso:
    id: int

    id_usuario_responsavel: int
    usuario_responsavel: "Usuario"
    area_direito: str
    sub_area: str | None
    clientes: list["Atendido"]

    id_orientador: int | None
    orientador: "Usuario | None"
    id_estagiario: int | None
    estagiario: "Usuario | None"
    id_colaborador: int | None
    colaborador: "Usuario | None"

    data_criacao: datetime
    id_criado_por: int
    criado_por: "Usuario"

    data_modificacao: datetime | None
    id_modificado_por: int | None
    modificado_por: "Usuario | None"

    situacao_deferimento: str
    justif_indeferimento: str | None
    status: bool
    descricao: str | None
    numero_ultimo_processo: int | None

    def __post_init__(self):
        return

    @staticmethod
    def from_sqlalchemy(caso: "CasoSchema") -> "Caso":
        return Caso(
            id=caso.id,
            id_usuario_responsavel=caso.id_usuario_responsavel,
            usuario_responsavel=caso.usuario_responsavel,
            area_direito=caso.area_direito,
            sub_area=caso.sub_area,
            clientes=caso.clientes,
            id_orientador=caso.id_orientador,
            orientador=caso.orientador,
            id_estagiario=caso.id_estagiario,
            estagiario=caso.estagiario,
            id_colaborador=caso.id_colaborador,
            colaborador=caso.colaborador,
            data_criacao=caso.data_criacao,
            id_criado_por=caso.id_criado_por,
            criado_por=caso.criado_por,
            data_modificacao=caso.data_modificacao,
            id_modificado_por=caso.id_modificado_por,
            modificado_por=caso.modificado_por,
            situacao_deferimento=caso.situacao_deferimento,
            justif_indeferimento=caso.justif_indeferimento,
            status=caso.status,
            descricao=caso.descricao,
            numero_ultimo_processo=caso.numero_ultimo_processo,
        )

    def set_sub_areas(
        self, area_direito: str, sub_area: str, sub_area_admin: str
    ) -> None:
        """Set sub areas based on the area of law"""
        if area_direito == "civel":
            self.sub_area = sub_area
        elif area_direito == "administrativo":
            self.sub_area = sub_area_admin
        else:
            self.sub_area = None
