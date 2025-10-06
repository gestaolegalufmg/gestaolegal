from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.models.assistido import Assistido
from gestaolegal.models.base_model import BaseModel
from gestaolegal.models.endereco import Endereco

if TYPE_CHECKING:
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


class Atendido(BaseModel):
    id: int

    orientacoes_juridicas: list["OrientacaoJuridica"] | None = None
    casos: list["Caso"] | None = None
    endereco: "Endereco | None" = None

    nome: str
    data_nascimento: date
    cpf: str
    cnpj: str | None
    endereco_id: int | None
    telefone: str | None
    celular: str
    email: str
    estado_civil: str

    como_conheceu: str
    indicacao_orgao: str | None
    procurou_outro_local: str
    procurou_qual_local: str | None
    obs: str | None
    pj_constituida: str
    repres_legal: bool | None
    nome_repres_legal: str | None
    cpf_repres_legal: str | None
    contato_repres_legal: str | None
    rg_repres_legal: str | None
    nascimento_repres_legal: date | None
    pretende_constituir_pj: str | None
    status: int

    assistido: "Assistido | None" = None
