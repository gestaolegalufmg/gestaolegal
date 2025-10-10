from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistido_pessoa_juridica import AssistidoPessoaJuridica


@dataclass
class Assistido:
    id_atendido: int
    sexo: str
    profissao: str
    raca: str
    rg: str
    grau_instrucao: str
    salario: float
    beneficio: str
    contribui_inss: str
    qtd_pessoas_moradia: int
    renda_familiar: float
    participacao_renda: str
    tipo_moradia: str
    possui_outros_imoveis: bool
    possui_veiculos: bool
    doenca_grave_familia: str
    
    id: int | None = None
    qual_beneficio: str | None = None
    quantos_imoveis: int | None = None
    possui_veiculos_obs: str | None = None
    quantos_veiculos: int | None = None
    ano_veiculo: str | None = None
    pessoa_doente: str | None = None
    pessoa_doente_obs: str | None = None
    gastos_medicacao: float | None = None
    obs: str | None = None
    assistido_pessoa_juridica: "AssistidoPessoaJuridica | None" = None
