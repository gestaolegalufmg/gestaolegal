import logging
from datetime import datetime
from typing import cast

from gestaolegal.database.session import transaction
from gestaolegal.exceptions import BusinessLogicException, NotFoundException
from gestaolegal.models.fila_atendimento import FilaAtendimento, FilaAtendimentoItem
from gestaolegal.models.fila_atendimento_input import AdicionarFilaInput
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.fila_atendimento_repository import (
    FilaAtendimentoRepository,
)

logger = logging.getLogger(__name__)

STATUS_AGUARDANDO = 0
STATUS_EM_ATENDIMENTO = 1
STATUS_CONCLUIDO = 2

STATUS_LABELS = {
    STATUS_AGUARDANDO: "Aguardando",
    STATUS_EM_ATENDIMENTO: "Em Atendimento",
    STATUS_CONCLUIDO: "Concluído",
}


class FilaAtendimentoService:
    repository: FilaAtendimentoRepository
    atendido_repository: AtendidoRepository

    def __init__(self):
        self.repository = FilaAtendimentoRepository()
        self.atendido_repository = AtendidoRepository()

    def get_fila(self) -> list[FilaAtendimentoItem]:
        entradas = self.repository.get_active()
        atendido_ids = [e.id_atendido for e in entradas]
        atendidos = self.atendido_repository.get_by_ids(atendido_ids)
        atendido_map = {cast(int, a.id): a for a in atendidos if a.id is not None}

        items: list[FilaAtendimentoItem] = []
        posicao = 0
        for e in entradas:
            atendido = atendido_map.get(e.id_atendido)
            if e.status == STATUS_AGUARDANDO:
                posicao += 1
                posicao_atual: int | None = posicao
            else:
                posicao_atual = None
            items.append(
                FilaAtendimentoItem(
                    id=cast(int, e.id),
                    senha=e.senha,
                    posicao=posicao_atual,
                    tipo=e.tipo,
                    prioridade=e.prioridade,
                    status=e.status,
                    status_label=STATUS_LABELS.get(e.status, "Desconhecido"),
                    data_criacao=e.data_criacao,
                    id_atendido=e.id_atendido,
                    atendido_nome=atendido.nome if atendido else "—",
                    atendido_cpf=atendido.cpf if atendido else "",
                )
            )
        return items

    def adicionar(self, data: AdicionarFilaInput) -> list[FilaAtendimentoItem]:
        logger.info(f"Adding atendido {data.id_atendido} to fila as {data.tipo}")
        atendido = self.atendido_repository.find_by_id(data.id_atendido)
        if not atendido:
            raise NotFoundException(resource="Atendido", resource_id=data.id_atendido)

        with transaction():
            senha = f"{self.repository.count_all() + 1:03d}"
            self.repository.create(
                {
                    "psicologia": 1 if data.tipo == "Atendimento Psicológico" else 0,
                    "id_atendido": data.id_atendido,
                    "prioridade": data.prioridade,
                    "senha": senha,
                    "data_criacao": datetime.now(),
                    "status": STATUS_AGUARDANDO,
                    "tipo": data.tipo,
                }
            )
        return self.get_fila()

    def chamar_proximo(self) -> list[FilaAtendimentoItem]:
        logger.info("Chamando próximo da fila de atendimento")
        em_atendimento = self.repository.find_em_atendimento()
        proximo = self.repository.find_proximo_aguardando()

        if not em_atendimento and not proximo:
            raise BusinessLogicException(
                message="Não há ninguém na fila de atendimento",
                error_code="FILA_VAZIA",
            )

        with transaction():
            for entrada in em_atendimento:
                self.repository.update(
                    cast(int, entrada.id), {"status": STATUS_CONCLUIDO}
                )
            if proximo:
                self.repository.update(
                    cast(int, proximo.id), {"status": STATUS_EM_ATENDIMENTO}
                )
        return self.get_fila()

    def concluir(self, id: int) -> list[FilaAtendimentoItem]:
        entrada = self._get_or_404(id)
        with transaction():
            self.repository.update(cast(int, entrada.id), {"status": STATUS_CONCLUIDO})
        return self.get_fila()

    def remover(self, id: int) -> list[FilaAtendimentoItem]:
        entrada = self._get_or_404(id)
        with transaction():
            self.repository.delete(cast(int, entrada.id))
        return self.get_fila()

    def _get_or_404(self, id: int) -> FilaAtendimento:
        entrada = self.repository.find_by_id(id)
        if not entrada:
            raise NotFoundException(resource="Fila de Atendimento", resource_id=id)
        return entrada
