from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gestaolegal.models.assistido import Assistido
    from gestaolegal.models.caso import Caso
    from gestaolegal.models.endereco import Endereco
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica


@dataclass
class Atendido:
    nome: str
    data_nascimento: date
    cpf: str
    celular: str
    email: str
    estado_civil: str
    como_conheceu: str
    procurou_outro_local: str
    pj_constituida: str
    status: int

    id: int | None = None
    cnpj: str | None = None
    endereco_id: int | None = None
    telefone: str | None = None
    indicacao_orgao: str | None = None
    procurou_qual_local: str | None = None
    obs: str | None = None
    repres_legal: bool | None = None
    nome_repres_legal: str | None = None
    cpf_repres_legal: str | None = None
    contato_repres_legal: str | None = None
    rg_repres_legal: str | None = None
    nascimento_repres_legal: date | None = None
    pretende_constituir_pj: str | None = None
    orientacoes_juridicas: list["OrientacaoJuridica"] | None = None
    casos: list["Caso"] | None = None
    endereco: "Endereco | None" = None
    assistido: "Assistido | None" = None
