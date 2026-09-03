import logging
from datetime import datetime
from typing import Iterable

from gestaolegal.common import PageParams, PaginatedResult
from gestaolegal.database.session import transaction
from gestaolegal.exceptions import NotFoundException
from gestaolegal.models.notificacao import NotificacaoListItem, TipoNotificacao
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.notificacao_repository import NotificacaoRepository

logger = logging.getLogger(__name__)

# Como na v2, orientadores e estagiários também recebem os avisos gerais
# (id_usu_notificar nulo), hoje só a abertura do plantão.
PAPEIS_AVISOS_GERAIS = ("orient", "estag_direito")


class NotificacaoService:
    """Notificações internas (módulo "Notificações" da v2).

    Disparadas por: cadastro/edição de caso (responsável, orientador,
    estagiário e colaborador), novo evento (responsável do evento), novo
    lembrete (usuário do lembrete) e abertura do plantão (aviso geral).
    Quem executa a ação nunca é notificado da própria ação.
    """

    repository: NotificacaoRepository

    def __init__(self):
        self.repository = NotificacaoRepository()

    # ------------------------------------------------------------- consulta

    @staticmethod
    def _inclui_gerais(user: UserInfo) -> bool:
        return user.urole in PAPEIS_AVISOS_GERAIS

    def listar(
        self, user: UserInfo, page_params: PageParams
    ) -> PaginatedResult[NotificacaoListItem]:
        return self.repository.listar(user.id, self._inclui_gerais(user), page_params)

    def contar_nao_lidas(self, user: UserInfo) -> int:
        return self.repository.contar_nao_lidas(user.id, self._inclui_gerais(user))

    def marcar_lida(self, id: int, user: UserInfo) -> None:
        with transaction():
            ok = self.repository.marcar_lida(id, user.id, self._inclui_gerais(user))
        if not ok:
            raise NotFoundException(resource="Notificação", resource_id=id)

    def marcar_todas_lidas(self, user: UserInfo) -> int:
        with transaction():
            return self.repository.marcar_todas_lidas(
                user.id, self._inclui_gerais(user)
            )

    # -------------------------------------------------------------- disparo

    def notificar(
        self,
        tipo: TipoNotificacao,
        acao: str,
        executor_id: int,
        destinatarios: Iterable[int | None] = (),
        id_caso: int | None = None,
        id_referencia: int | None = None,
        geral: bool = False,
    ) -> int:
        """Cria uma notificação por destinatário (sem repetir e sem o executor).

        Valores vazios em `destinatarios` são ignorados. `geral=True` cria um
        único aviso sem destinatário (visto por orientadores e estagiários).
        Devolve quantas foram criadas. Chamar dentro da transação da origem.
        """
        agora = datetime.now()
        alvos: list[int | None] = [None] if geral else []
        vistos: set[int] = set()
        for dest in destinatarios:
            if not dest or dest in vistos or dest == executor_id:
                continue
            vistos.add(dest)
            alvos.append(dest)
        rows = []
        for dest in alvos:
            rows.append(
                {
                    "acao": acao,
                    "data": agora.date(),
                    "data_criacao": agora,
                    "id_executor_acao": executor_id,
                    "id_usu_notificar": dest,
                    "tipo": tipo,
                    "id_caso": id_caso,
                    "id_referencia": id_referencia,
                    "lida": False,
                }
            )
        self.repository.create_many(rows)
        if rows:
            logger.info(f"{len(rows)} notificação(ões) '{tipo}' criada(s) por {executor_id}")
        return len(rows)

    def caso_cadastrado(self, caso, executor_id: int) -> int:
        return self.notificar(
            "caso",
            f"Cadastrado no caso {caso.id}",
            executor_id,
            [
                caso.id_usuario_responsavel,
                caso.id_orientador,
                caso.id_estagiario,
                caso.id_colaborador,
            ],
            id_caso=caso.id,
        )

    def caso_editado(self, antes, depois, executor_id: int) -> int:
        """Avisa só quem passou a fazer parte do caso na edição."""
        campos = (
            "id_usuario_responsavel",
            "id_orientador",
            "id_estagiario",
            "id_colaborador",
        )
        novos = [
            getattr(depois, c)
            for c in campos
            if getattr(depois, c) and getattr(depois, c) != getattr(antes, c)
        ]
        return self.notificar(
            "caso", f"Cadastrado no caso {depois.id}", executor_id, novos, id_caso=depois.id
        )

    def evento_criado(self, evento, executor_id: int) -> int:
        if not evento.id_usuario_responsavel:
            return 0
        return self.notificar(
            "evento",
            f"Cadastrado no evento {evento.num_evento} do caso {evento.id_caso}",
            executor_id,
            [evento.id_usuario_responsavel],
            id_caso=evento.id_caso,
            id_referencia=evento.id,
        )

    def lembrete_criado(
        self, lembrete_id: int, num_lembrete: int, id_caso: int, id_usuario: int, executor_id: int
    ) -> int:
        return self.notificar(
            "lembrete",
            f"Cadastrado no lembrete {num_lembrete} do caso {id_caso}",
            executor_id,
            [id_usuario],
            id_caso=id_caso,
            id_referencia=lembrete_id,
        )

    def plantao_aberto(self, executor_id: int) -> int:
        return self.notificar("plantao", "Abertura do plantão", executor_id, geral=True)
