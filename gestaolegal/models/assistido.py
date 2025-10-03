from dataclasses import dataclass
from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.assistido_pessoa_juridica import AssistidoPessoaJuridica


@dataclass(frozen=True)
class Assistido(BaseModel):
    id: int
    id_atendido: int
    sexo: str
    profissao: str
    raca: str
    rg: str
    grau_instrucao: str
    salario: float
    beneficio: str
    qual_beneficio: str | None
    contribui_inss: str
    qtd_pessoas_moradia: int
    renda_familiar: float
    participacao_renda: str
    tipo_moradia: str
    possui_outros_imoveis: bool
    quantos_imoveis: int | None
    possui_veiculos: bool
    possui_veiculos_obs: str | None
    quantos_veiculos: int | None
    ano_veiculo: str | None
    doenca_grave_familia: str
    pessoa_doente: str | None
    pessoa_doente_obs: str | None
    gastos_medicacao: float | None
    obs: str | None

    assistido_pessoa_juridica: "AssistidoPessoaJuridica | None" = None

    def __post_init__(self):
        return
        if self.possui_veiculos:
            if (
                self.possui_veiculos_obs is None
                or self.quantos_veiculos is None
                or self.ano_veiculo is None
            ):
                raise ValueError(
                    "Os campos possui_veiculos_obs, quantos_veiculos e ano_veiculo são obrigatórios se possui_veiculos for True"
                )
        else:
            raise ValueError(
                "Os campos possui_veiculos_obs, quantos_veiculos e ano_veiculo são obrigatórios se possui_veiculos for True"
            )

        if self.doenca_grave_familia == "sim":
            if (
                self.pessoa_doente is None
                or self.pessoa_doente_obs is None
                or self.gastos_medicacao is None
            ):
                raise ValueError(
                    "Os campos pessoa_doente, pessoa_doente_obs e gastos_medicacao são obrigatórios se doenca_grave_familia for True"
                )

        if self.pessoa_doente is None and self.pessoa_doente_obs is not None:
            raise ValueError(
                "Os campos pessoa_doente e gastos_medicacao são obrigatórios se doenca_grave_familia for True"
            )
