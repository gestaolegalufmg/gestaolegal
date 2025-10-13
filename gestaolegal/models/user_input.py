from gestaolegal.models.base_model import BaseModel


class UserCreateInput(BaseModel):
    email: str
    urole: str
    nome: str
    sexo: str
    rg: str
    cpf: str
    profissao: str
    estado_civil: str
    nascimento: str
    telefone: str | None
    celular: str
    oab: str | None
    obs: str | None
    data_entrada: str
    data_saida: str | None
    matricula: str | None
    bolsista: bool
    tipo_bolsa: str | None
    horario_atendimento: str | None
    suplente: str | None
    ferias: str | None
    cert_atuacao_DAJ: str
    inicio_bolsa: str | None
    fim_bolsa: str | None

    logradouro: str
    numero: str
    complemento: str | None = None
    bairro: str
    cep: str
    cidade: str
    estado: str


class UserUpdateInput(BaseModel):
    email: str | None = None
    urole: str | None = None
    nome: str | None = None
    sexo: str | None = None
    rg: str | None = None
    cpf: str | None = None
    profissao: str | None = None
    estado_civil: str | None = None
    nascimento: str | None = None
    telefone: str | None = None
    celular: str | None = None
    oab: str | None = None
    obs: str | None = None
    data_entrada: str | None = None
    data_saida: str | None = None
    matricula: str | None = None
    bolsista: bool | None = None
    tipo_bolsa: str | None = None
    horario_atendimento: str | None = None
    suplente: str | None = None
    ferias: str | None = None
    cert_atuacao_DAJ: str | None = None
    inicio_bolsa: str | None = None
    fim_bolsa: str | None = None

    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cep: str | None = None
    cidade: str | None = None
    estado: str | None = None
