from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from gestaolegal.common.constants import como_conheceu_daj

if TYPE_CHECKING:
    from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
    from gestaolegal.schemas.atendido import AtendidoSchema
    from gestaolegal.schemas.caso import Caso
    from gestaolegal.schemas.endereco import EnderecoSchema


@dataclass(frozen=True)
class Atendido:
    id: int

    orientacoes_juridicas: list["OrientacaoJuridica"]
    casos: list["Caso"]
    endereco: "EnderecoSchema | None"

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
    repres_legal: str | None
    nome_repres_legal: str | None
    cpf_repres_legal: str | None
    contato_repres_legal: str | None
    rg_repres_legal: str | None
    nascimento_repres_legal: date | None
    pretende_constituir_pj: str | None
    status: int

    def __post_init__(self):
        return
        if self.como_conheceu == como_conheceu_daj["ORGAOSPUBLICOS"][0]:
            for field, msg in [
                (
                    "indicacao_orgao",
                    "O campo 'indicacao_orgao' é obrigatório se 'como_conheceu' for 'Orgaos Públicos'",
                ),
                (
                    "procurou_outro_local",
                    "O campo 'procurou_outro_local' é obrigatório se 'como_conheceu' for 'Orgaos Públicos'",
                ),
                (
                    "procurou_qual_local",
                    "O campo 'procurou_qual_local' é obrigatório se 'como_conheceu' for 'Orgaos Públicos'",
                ),
                (
                    "pj_constituida",
                    "O campo 'pj_constituida' é obrigatório se 'como_conheceu' for 'Orgaos Públicos'",
                ),
            ]:
                if getattr(self, field) is None:
                    raise ValueError(msg)

        if self.pj_constituida:
            if self.cnpj is None:
                raise ValueError(
                    "O campo 'cnpj' é obrigatório se 'pj_constituida' for verdadeiro"
                )
            if self.repres_legal is None:
                raise ValueError(
                    "O campo 'repres_legal' é obrigatório se 'pj_constituida' for verdadeiro"
                )

        if (not self.repres_legal) and self.pj_constituida:
            required_fields = [
                (
                    "nome_repres_legal",
                    "O campo 'nome_repres_legal' é obrigatório se 'repres_legal' for falso e 'pj_constituida' for verdadeiro",
                ),
                (
                    "cpf_repres_legal",
                    "O campo 'cpf_repres_legal' é obrigatório se 'repres_legal' for falso e 'pj_constituida' for verdadeiro",
                ),
                (
                    "contato_repres_legal",
                    "O campo 'contato_repres_legal' é obrigatório se 'repres_legal' for falso e 'pj_constituida' for verdadeiro",
                ),
                (
                    "rg_repres_legal",
                    "O campo 'rg_repres_legal' é obrigatório se 'repres_legal' for falso e 'pj_constituida' for verdadeiro",
                ),
                (
                    "nascimento_repres_legal",
                    "O campo 'nascimento_repres_legal' é obrigatório se 'repres_legal' for falso e 'pj_constituida' for verdadeiro",
                ),
            ]
            for field, msg in required_fields:
                if getattr(self, field) is None:
                    raise ValueError(msg)

        if self.procurou_outro_local:
            if self.procurou_qual_local is None:
                raise ValueError(
                    "O campo 'procurou_qual_local' é obrigatório se 'procurou_outro_local' for verdadeiro"
                )

    @staticmethod
    def from_sqlalchemy(atendido: "AtendidoSchema") -> "Atendido":
        return Atendido(
            id=atendido.id,
            orientacoes_juridicas=atendido.orientacoesJuridicas,
            casos=atendido.casos,
            endereco=atendido.endereco,
            nome=atendido.nome,
            data_nascimento=atendido.data_nascimento,
            cpf=atendido.cpf,
            cnpj=atendido.cnpj,
            endereco_id=atendido.endereco_id,
            telefone=atendido.telefone,
            celular=atendido.celular,
            email=atendido.email,
            estado_civil=atendido.estado_civil,
            como_conheceu=atendido.como_conheceu,
            indicacao_orgao=atendido.indicacao_orgao,
            procurou_outro_local=atendido.procurou_outro_local,
            procurou_qual_local=atendido.procurou_qual_local,
            obs=atendido.obs,
            pj_constituida=atendido.pj_constituida,
            repres_legal=atendido.repres_legal,
            nome_repres_legal=atendido.nome_repres_legal,
            cpf_repres_legal=atendido.cpf_repres_legal,
            contato_repres_legal=atendido.contato_repres_legal,
            rg_repres_legal=atendido.rg_repres_legal,
            nascimento_repres_legal=atendido.nascimento_repres_legal,
            pretende_constituir_pj=atendido.pretende_constituir_pj,
            status=atendido.status,
        )
