from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.schemas.assistido import AssistidoSchema


@dataclass(frozen=True)
class Assistido:
    id: int | None
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

    @staticmethod
    def from_sqlalchemy(assistido: "AssistidoSchema") -> "Assistido":
        return Assistido(
            id=assistido.id,
            id_atendido=assistido.id_atendido,
            sexo=assistido.sexo,
            profissao=assistido.profissao,
            raca=assistido.raca,
            rg=assistido.rg,
            grau_instrucao=assistido.grau_instrucao,
            salario=assistido.salario,
            beneficio=assistido.beneficio,
            qual_beneficio=assistido.qual_beneficio,
            contribui_inss=assistido.contribui_inss,
            qtd_pessoas_moradia=assistido.qtd_pessoas_moradia,
            renda_familiar=assistido.renda_familiar,
            participacao_renda=assistido.participacao_renda,
            tipo_moradia=assistido.tipo_moradia,
            possui_outros_imoveis=assistido.possui_outros_imoveis,
            quantos_imoveis=assistido.quantos_imoveis,
            possui_veiculos=assistido.possui_veiculos,
            possui_veiculos_obs=assistido.possui_veiculos_obs,
            quantos_veiculos=assistido.quantos_veiculos,
            ano_veiculo=assistido.ano_veiculo,
            doenca_grave_familia=assistido.doenca_grave_familia,
            pessoa_doente=assistido.pessoa_doente,
            pessoa_doente_obs=assistido.pessoa_doente_obs,
            gastos_medicacao=assistido.gastos_medicacao,
            obs=assistido.obs,
        )
