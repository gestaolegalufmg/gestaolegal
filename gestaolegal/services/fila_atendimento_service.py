import logging
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from gestaolegal.exceptions import NotFoundException, ValidationException
from gestaolegal.models.fila_atendimento import (
    SENHA_PREFIXOS,
    FilaPrioridade,
    FilaStatus,
    ListFilaAtendimento,
)
from gestaolegal.models.fila_atendimento_input import FilaAtendimentoCreateInput
from gestaolegal.repositories.fila_atendimento_repository import (
    FilaAtendimentoRepository,
)

logger = logging.getLogger(__name__)

# A fila é organizada por dia de Brasília (senhas zeram à 00h local, não em GMT).
# O servidor roda em UTC, então precisamos converter explicitamente.
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def _agora_brasilia() -> datetime:
    """Data/hora atual no fuso de Brasília, como datetime "naive" (sem tzinfo).

    Gravamos os timestamps da fila já no horário de parede de Brasília para que
    a filtragem por dia (_intervalo_do_dia) seja consistente com o que é exibido.
    """
    return datetime.now(FUSO_BRASILIA).replace(tzinfo=None)


def _hoje_brasilia() -> date:
    return _agora_brasilia().date()


class FilaAtendimentoService:
    repository: FilaAtendimentoRepository

    def __init__(self):
        self.repository = FilaAtendimentoRepository()

    def _intervalo_do_dia(self, dia: date | None = None) -> tuple[datetime, datetime]:
        """Início e fim (inclusivos) do dia informado (padrão: hoje em Brasília)."""
        dia = dia or _hoje_brasilia()
        return (
            datetime.combine(dia, time(0, 0, 0)),
            datetime.combine(dia, time(23, 59, 59, 999999)),
        )

    def _proximo_numero(self, prioridade: int) -> int:
        inicio, fim = self._intervalo_do_dia()
        total = self.repository.count_by_prioridade_no_periodo(prioridade, inicio, fim)
        return total + 1

    def _formatar_senha(self, prioridade: int, numero: int) -> str:
        prefixo = SENHA_PREFIXOS[prioridade]
        return f"{prefixo}{numero:02d}"

    def preview_senha(self, prioridade: int) -> str:
        """Prévia da senha que seria atribuída ao próximo atendido do grupo."""
        if prioridade not in FilaPrioridade.VALORES:
            raise ValidationException(
                "prioridade deve ser 0 (normal), 1 (prioridade) ou 2 (super prioridade)",
                field="prioridade",
            )
        return self._formatar_senha(prioridade, self._proximo_numero(prioridade))

    def get_fila_hoje(self) -> dict[str, Any]:
        """Retorna a fila do dia separada em ativos e concluídos (chamados/cancelados)."""
        hoje = _hoje_brasilia()
        inicio, fim = self._intervalo_do_dia(hoje)
        rows = self.repository.list_no_periodo(inicio, fim)

        itens = [ListFilaAtendimento(**row) for row in rows]

        na_fila = [i for i in itens if i.status == FilaStatus.NA_FILA]
        concluidos = [i for i in itens if i.status != FilaStatus.NA_FILA]

        # Fila ativa: maior prioridade primeiro; em empate, quem entrou antes.
        na_fila.sort(
            key=lambda i: (
                -i.prioridade,
                i.data_criacao or datetime.max,
            )
        )

        # Atendidos/cancelados: ordenados pelo momento em que saíram da fila
        # (mais antigo primeiro, ordem cronológica). Registros históricos sem
        # data_saida usam a data de criação como referência.
        concluidos.sort(
            key=lambda i: (i.data_saida or i.data_criacao or datetime.min),
        )

        return {
            "data": hoje.isoformat(),
            "fila": [i.__dict__ for i in na_fila],
            "atendidos_cancelados": [i.__dict__ for i in concluidos],
        }

    def _item_por_id(self, fila_id: int) -> ListFilaAtendimento:
        registro = self.repository.find_by_id(fila_id)
        if not registro:
            raise NotFoundException(resource="FilaAtendimento", resource_id=fila_id)
        inicio, fim = self._intervalo_do_dia()
        for row in self.repository.list_no_periodo(inicio, fim):
            if row["id"] == fila_id:
                return ListFilaAtendimento(**row)
        # Registro de outro dia: monta a partir do próprio registro.
        return ListFilaAtendimento(
            id=registro.id,
            id_atendido=registro.id_atendido,
            nome=None,
            senha=registro.senha,
            prioridade=registro.prioridade,
            psicologia=registro.psicologia,
            status=registro.status,
            data_criacao=registro.data_criacao,
            data_saida=registro.data_saida,
        )

    def criar(self, dados: FilaAtendimentoCreateInput) -> ListFilaAtendimento:
        logger.info(
            f"Incluindo atendido {dados.id_atendido} na fila "
            f"(prioridade={dados.prioridade}, psicologia={dados.psicologia})"
        )
        numero = self._proximo_numero(dados.prioridade)
        senha = self._formatar_senha(dados.prioridade, numero)

        novo = {
            "id_atendido": dados.id_atendido,
            "prioridade": dados.prioridade,
            "psicologia": 1 if dados.psicologia else 0,
            "senha": senha,
            "status": FilaStatus.NA_FILA,
            "data_criacao": _agora_brasilia(),
            "data_saida": None,
        }

        fila_id = self.repository.create(novo)
        logger.info(f"Atendido incluído na fila com id {fila_id} e senha {senha}")
        return self._item_por_id(fila_id)

    def chamar(self, fila_id: int) -> ListFilaAtendimento:
        return self._concluir(fila_id, FilaStatus.CHAMADO)

    def cancelar(self, fila_id: int) -> ListFilaAtendimento:
        return self._concluir(fila_id, FilaStatus.CANCELADO)

    def _concluir(self, fila_id: int, novo_status: int) -> ListFilaAtendimento:
        registro = self.repository.find_by_id(fila_id)
        if not registro:
            raise NotFoundException(resource="FilaAtendimento", resource_id=fila_id)
        if registro.status != FilaStatus.NA_FILA:
            raise ValidationException("Atendido já saiu da fila", field="status")

        self.repository.update(
            fila_id,
            {"status": novo_status, "data_saida": _agora_brasilia()},
        )
        logger.info(f"Fila {fila_id} atualizada para status {novo_status}")
        return self._item_por_id(fila_id)
