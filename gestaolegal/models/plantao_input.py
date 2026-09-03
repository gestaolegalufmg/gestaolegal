from datetime import date, datetime

from pydantic import field_validator, model_validator

from gestaolegal.models.base_model import BaseModel


class MarcarDiaInput(BaseModel):
    data: date


class ConfiguracaoPlantaoInput(BaseModel):
    """Configuração completa do plantão: dias abertos e janela de marcação."""

    dias: list[date]
    data_abertura: datetime
    data_fechamento: datetime

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
