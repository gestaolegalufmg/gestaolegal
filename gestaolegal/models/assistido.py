from typing import TYPE_CHECKING

from gestaolegal.models.base_model import BaseModel

if TYPE_CHECKING:
    from gestaolegal.models.assistido_pessoa_juridica import AssistidoPessoaJuridica


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
