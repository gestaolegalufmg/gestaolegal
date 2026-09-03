from typing import Literal

from pydantic import Field

from gestaolegal.models.base_model import BaseModel


class RegistrarPresencaInput(BaseModel):
    # A pessoa pode ajustar o horário no formulário; a data é sempre hoje.
    hora: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class ConfirmacaoItemInput(BaseModel):
    id: int
    confirmacao: Literal["confirmar", "divergencia", "ausencia"]


class ConfirmacaoBatchInput(BaseModel):
    presencas: list[ConfirmacaoItemInput] = []
    plantoes: list[ConfirmacaoItemInput] = []
