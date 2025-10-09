from gestaolegal.models.base_model import BaseModel


class AssistidoCreateInput(BaseModel):
    sexo: str
    profissao: str
    raca: str
    rg: str
    grau_instrucao: str
    salario: float
    beneficio: str
    qual_beneficio: str | None = None
    contribui_inss: str
    qtd_pessoas_moradia: int
    renda_familiar: float
    participacao_renda: str
    tipo_moradia: str
    possui_outros_imoveis: bool
    quantos_imoveis: int | None = None
    possui_veiculos: bool
    possui_veiculos_obs: str | None = None
    quantos_veiculos: int | None = None
    ano_veiculo: str | None = None
    doenca_grave_familia: str
    pessoa_doente: str | None = None
    pessoa_doente_obs: str | None = None
    gastos_medicacao: float | None = None
    obs: str | None = None


class AssistidoUpdateInput(BaseModel):
    sexo: str | None = None
    profissao: str | None = None
    raca: str | None = None
    rg: str | None = None
    grau_instrucao: str | None = None
    salario: float | None = None
    beneficio: str | None = None
    qual_beneficio: str | None = None
    contribui_inss: str | None = None
    qtd_pessoas_moradia: int | None = None
    renda_familiar: float | None = None
    participacao_renda: str | None = None
    tipo_moradia: str | None = None
    possui_outros_imoveis: bool | None = None
    quantos_imoveis: int | None = None
    possui_veiculos: bool | None = None
    possui_veiculos_obs: str | None = None
    quantos_veiculos: int | None = None
    ano_veiculo: str | None = None
    doenca_grave_familia: str | None = None
    pessoa_doente: str | None = None
    pessoa_doente_obs: str | None = None
    gastos_medicacao: float | None = None
    obs: str | None = None
