from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import Field, field_validator, model_validator

from gestaolegal.models.base_model import BaseModel


class MarcarDiaInput(BaseModel):
    data: date


class ConfiguracaoPlantaoInput(BaseModel):
    """Configuração completa do plantão: dias abertos e janela de marcação."""

    dias: list[date]
    data_abertura: datetime
    data_fechamento: datetime
    nome: str = Field(default="Escala de plantão", min_length=1, max_length=150)

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, value):
        if not value.strip():
            raise ValueError("Informe o nome da escala")
        return value.strip()

    @field_validator("data_abertura", "data_fechamento")
    @classmethod
    def horario_brasilia(cls, value):
        if value.tzinfo:
            return value.astimezone(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
        return value

    @field_validator("dias")
    @classmethod
    def validate_dias(cls, value: list[date]) -> list[date]:
        if len(set(value)) != len(value):
            raise ValueError("Há datas repetidas na duração do plantão")
        return sorted(value)

    @model_validator(mode="after")
    def validate_janela(self) -> "ConfiguracaoPlantaoInput":
        if self.data_fechamento <= self.data_abertura:
            raise ValueError(
                "A data de fechamento deve ser posterior à data de abertura"
            )
        return self
