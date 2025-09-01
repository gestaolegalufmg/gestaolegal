from sqlalchemy import Column, ForeignKey, Integer, Table

from gestaolegal.schemas.base import Base

associacao_casos_atendidos = Table(
    "casos_atendidos",
    Base.metadata,
    Column("id_caso", Integer, ForeignKey("casos.id", ondelete="CASCADE")),
    Column("id_atendido", Integer, ForeignKey("atendidos.id", ondelete="CASCADE")),
)

# Import association schemas to ensure they are registered with SQLAlchemy
from gestaolegal.schemas.assistencia_judiciaria_x_orientacao_juridica import (
    AssistenciaJudiciaria_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.atendido_x_orientacao_juridica import (
    Atendido_xOrientacaoJuridicaSchema,
)
