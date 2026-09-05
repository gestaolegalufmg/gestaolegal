import logging
from datetime import datetime

from gestaolegal.database.session import transaction
from gestaolegal.exceptions import NotFoundException, ValidationException
from gestaolegal.models.unidade import Unidade
from gestaolegal.models.unidade_input import UnidadeCreateInput, UnidadeUpdateInput
from gestaolegal.repositories.unidade_repository import UnidadeRepository

logger = logging.getLogger(__name__)


class UnidadeService:
    repository: UnidadeRepository

    def __init__(self):
        self.repository = UnidadeRepository()

    def listar(self, incluir_inativas: bool = False) -> list[Unidade]:
        return self.repository.listar(incluir_inativas=incluir_inativas)

    def find_by_id(self, id: int) -> Unidade:
        unidade = self.repository.find_by_id(id)
        if not unidade:
            raise NotFoundException(resource="Unidade", resource_id=id)
        return unidade

    def criar(self, dados: UnidadeCreateInput) -> Unidade:
        nome = dados.nome.strip()
        sigla = dados.sigla.strip().upper()
        self._validar_texto(nome, sigla)

        with transaction():
            if self.repository.existe_com_nome_ou_sigla(nome, sigla):
                raise ValidationException("Já existe unidade com esse nome ou sigla")

            unidade_id = self.repository.create(
                {
                    "nome": nome,
                    "sigla": sigla,
                    "ativa": dados.ativa,
                    "criado": datetime.now(),
                }
            )

        logger.info(f"Unidade {unidade_id} criada")
        return self.find_by_id(unidade_id)

    def atualizar(self, id: int, dados: UnidadeUpdateInput) -> Unidade:
        atual = self.find_by_id(id)

        nome = dados.nome.strip() if dados.nome is not None else atual.nome
        sigla = dados.sigla.strip().upper() if dados.sigla is not None else atual.sigla
        ativa = dados.ativa if dados.ativa is not None else atual.ativa
        self._validar_texto(nome, sigla)

        with transaction():
            if self.repository.existe_com_nome_ou_sigla(nome, sigla, ignorar_id=id):
                raise ValidationException("Já existe unidade com esse nome ou sigla")

            self.repository.update(id, {"nome": nome, "sigla": sigla, "ativa": ativa})

        logger.info(f"Unidade {id} atualizada")
        return self.find_by_id(id)

    def _validar_texto(self, nome: str, sigla: str) -> None:
        if not nome:
            raise ValidationException("Nome é obrigatório", field="nome")
        if not sigla:
            raise ValidationException("Sigla é obrigatória", field="sigla")
