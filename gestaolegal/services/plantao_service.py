import json
import logging
from datetime import date
from functools import wraps
from typing import Any

from gestaolegal.exceptions import (
    BusinessLogicException,
    NotFoundException,
    ValidationException,
)
from gestaolegal.models.plantao import (
    LIMITE_MARCACOES,
    LIMITE_MARCACOES_POR_UROLE,
    UROLES_IGNORAM_JANELA,
    VAGAS_POR_UROLE,
)
from gestaolegal.models.plantao_input import ConfiguracaoPlantaoInput, MarcarDiaInput
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.plantao_repository import PlantaoRepository
from gestaolegal.services.notificacao_service import NotificacaoService
from gestaolegal.utils.request_context import RequestContext
from gestaolegal.utils.tempo import agora_brasilia

logger = logging.getLogger(__name__)


def transacao_escala(func):
    @wraps(func)
    def executar(self, *args, **kwargs):
        try:
            resultado = func(self, *args, **kwargs)
            self.repository.session.commit()
            return resultado
        except Exception:
            self.repository.session.rollback()
            raise

    return executar


class PlantaoService:
    repository: PlantaoRepository

    def __init__(self, escala_id: int | None = None):
        self.repository = PlantaoRepository()
        self.repository.escala_id = escala_id
        self.explicita = escala_id is not None

    def _unidade(self) -> int:
        return RequestContext.get_unidade_ativa()

    # --- janela de marcação ----------------------------------------------

    def _selecionar(self, lock=False):
        registro = self.repository.get_plantao(unidade_id=self._unidade(), lock=lock)
        if not registro and self.explicita:
            raise NotFoundException(
                resource="Escala", resource_id=self.repository.escala_id
            )
        self.repository.escala_id = registro.id if registro else -1
        self.repository.incluir_inativos = bool(registro and registro.legado)
        return registro

    def _situacao(self, registro):
        if registro.cancelado:
            return "cancelada"
        if registro.legado:
            return "legado"
        agora = agora_brasilia()
        if not registro.data_abertura or agora < registro.data_abertura:
            return "inscricoes_futuras"
        if not registro.data_fechamento or agora >= registro.data_fechamento:
            return "inscricoes_encerradas"
        return "inscricoes_abertas"

    def _esta_aberto(self):
        registro = self.repository.get_plantao(unidade_id=self._unidade())
        return bool(registro and self._situacao(registro) == "inscricoes_abertas")

    def _pode_alterar(self, registro, user):
        return bool(
            registro
            and not registro.cancelado
            and not registro.legado
            and (
                self._situacao(registro) == "inscricoes_abertas"
                or user.urole in UROLES_IGNORAM_JANELA
            )
        )

    def _auditar(self, registro, acao, executor_id, detalhes=None):
        historico = json.loads(registro.historico or "[]")
        historico.append(
            {
                "data": agora_brasilia().isoformat(),
                "usuario_id": executor_id,
                "acao": acao,
                "detalhes": detalhes,
            }
        )
        self.repository.update_plantao(
            registro.id,
            {"historico": json.dumps(historico, ensure_ascii=False, default=str)},
        )

    def _historico(self, registro, user):
        if not registro or user.urole not in UROLES_IGNORAM_JANELA:
            return []
        from sqlalchemy import select

        from gestaolegal.database.tables import usuarios

        historico = json.loads(registro.historico or "[]")
        ids = {item["usuario_id"] for item in historico if item.get("usuario_id")}
        nomes = dict(
            self.repository.session.execute(
                select(usuarios.c.id, usuarios.c.nome).where(usuarios.c.id.in_(ids))
            ).all()
        )
        return [
            dict(
                item,
                usuario_nome=nomes.get(
                    item.get("usuario_id"), "Usuário não identificado"
                ),
            )
            for item in historico
        ]

    def listar_escalas(self):
        resultado = []
        for registro in self.repository.list_escalas(self._unidade()):
            self.repository.escala_id = registro.id
            self.repository.incluir_inativos = registro.legado
            dias = self.repository.list_dias(unidade_id=self._unidade())
            resultado.append(
                {
                    "id": registro.id,
                    "nome": registro.nome,
                    "unidade_id": registro.unidade_id,
                    "situacao": self._situacao(registro),
                    "legado": registro.legado,
                    "cancelado": registro.cancelado,
                    "data_abertura": registro.data_abertura.isoformat()
                    if registro.data_abertura
                    else None,
                    "data_fechamento": registro.data_fechamento.isoformat()
                    if registro.data_fechamento
                    else None,
                    "dias": [d.data.isoformat() for d in dias if d.data],
                }
            )
        return resultado

    @transacao_escala
    def cancelar(self, executor_id):
        registro = self._selecionar(lock=True)
        if not registro or registro.legado:
            raise ValidationException("Escala de legado é somente para consulta.")
        if not registro.cancelado:
            self.repository.update_plantao(registro.id, {"cancelado": True})
            self._auditar(registro, "cancelar", executor_id)
        return self.get_configuracao()

    # --- vagas -------------------------------------------------------------

    def _limite_marcacoes(self, urole: str) -> int:
        return LIMITE_MARCACOES_POR_UROLE.get(urole, LIMITE_MARCACOES)

    def _vagas_por_dia(
        self, dias: list[date], marcacoes: list[dict[str, Any]], urole: str
    ) -> dict[date, int | None]:
        """Vagas restantes em cada dia para quem tem o papel `urole`.

        `None` significa que o papel não tem limite. A regra de overbooking da
        v2 é preservada: se todos os dias abertos já estão lotados para aquele
        papel, a restrição é liberada em todos eles — senão ninguém mais
        conseguiria marcar plantão quando a escala enche.
        """
        limite = VAGAS_POR_UROLE.get(urole)
        if limite is None:
            return {dia: None for dia in dias}

        ocupacao = {dia: 0 for dia in dias}
        for marcacao in marcacoes:
            if marcacao["urole"] != urole:
                continue
            dia = marcacao["data_marcada"]
            if dia in ocupacao:
                ocupacao[dia] += 1

        todos_lotados = bool(dias) and all(ocupacao[dia] >= limite for dia in dias)
        if todos_lotados:
            return {dia: limite for dia in dias}

        return {dia: max(limite - ocupacao[dia], 0) for dia in dias}

    # --- leitura -----------------------------------------------------------

    def get_pagina(self, user: UserInfo) -> dict[str, Any]:
        """Tudo que a tela da escala precisa, em uma resposta só."""
        registro = self._selecionar()

        unidade_id = self._unidade()
        registro = self.repository.get_plantao(unidade_id=unidade_id)
        aberto = self._esta_aberto()
        dias = [
            dia.data
            for dia in self.repository.list_dias(unidade_id=unidade_id)
            if dia.data
        ]
        marcacoes = self.repository.list_marcacoes_ativas(unidade_id=unidade_id)
        if registro and registro.legado:
            dias = sorted(
                set(dias) | {m["data_marcada"] for m in marcacoes if m["data_marcada"]}
            )
        vagas = self._vagas_por_dia(dias, marcacoes, user.urole)

        meus_dias = self.repository.list_marcacoes_ativas_do_usuario(
            user.id, unidade_id=unidade_id
        )

        return {
            "plantao": {
                "id": registro.id if registro else None,
                "nome": registro.nome if registro else "Sem escala",
                "legado": registro.legado if registro else False,
                "cancelado": registro.cancelado if registro else False,
                "situacao": self._situacao(registro) if registro else "sem_escala",
                "data_abertura": registro.data_abertura if registro else None,
                "data_fechamento": registro.data_fechamento if registro else None,
                "aberto": aberto,
            },
            "pode_marcar": self._pode_alterar(registro, user),
            "historico": self._historico(registro, user),
            "limite_dias": self._limite_marcacoes(user.urole),
            # Qual plantão a pessoa está prestes a marcar (1º ou 2º). Conta só as
            # marcações ativas: na v2 o contador nunca voltava a 1 depois de
            # apagar os dias, porque as inativas continuavam sendo somadas.
            "numero_plantao": len(meus_dias) + 1,
            # Datas puras vão como "YYYY-MM-DD": o serializador do Flask
            # converteria `date` para RFC-1123 GMT, formato inconveniente para o
            # calendário do front comparar com o dia selecionado.
            "dias_abertos": [
                {
                    "data": dia.isoformat(),
                    "tem_vaga": vagas[dia] is None or vagas[dia] > 0,
                    "vagas_restantes": vagas[dia],
                }
                for dia in dias
            ],
            "escala": [
                {
                    "id": m["id"],
                    "ativo": m["status"],
                    "confirmacao": m["confirmacao"],
                    "data": m["data_marcada"].isoformat()
                    if m["data_marcada"]
                    else None,
                    "id_usuario": m["id_usuario"],
                    "nome": m["nome"] or "Usuário não identificado",
                    "urole": m["urole"],
                }
                for m in marcacoes
            ],
            "meus_dias": [
                {
                    "id": m.id,
                    "data_marcada": m.data_marcada.isoformat()
                    if m.data_marcada
                    else None,
                    "ativo": m.status,
                    "confirmacao": m.confirmacao,
                }
                for m in meus_dias
            ],
        }

    # --- marcação ----------------------------------------------------------

    @transacao_escala
    def marcar_dia(self, dados: MarcarDiaInput, user: UserInfo) -> dict[str, Any]:
        registro = self._selecionar(lock=True)

        if not self._pode_alterar(registro, user):
            raise BusinessLogicException(
                "As inscrições desta escala não estão abertas.", "PLANTAO_FECHADO"
            )

        unidade_id = self._unidade()
        dias = [
            dia.data
            for dia in self.repository.list_dias(unidade_id=unidade_id)
            if dia.data
        ]
        if dados.data not in dias:
            raise ValidationException(
                "Data selecionada não foi aberta para plantão.", field="data"
            )

        marcacoes = self.repository.list_marcacoes_ativas(unidade_id=unidade_id)
        vagas = self._vagas_por_dia(dias, marcacoes, user.urole)
        restantes = vagas[dados.data]
        if restantes is not None and restantes <= 0:
            raise BusinessLogicException(
                "Não há vagas disponíveis na data selecionada, tente outro dia.",
                "SEM_VAGAS",
            )

        meus_dias = self.repository.list_marcacoes_ativas_do_usuario(
            user.id, unidade_id=unidade_id
        )
        if len(meus_dias) >= self._limite_marcacoes(user.urole):
            raise BusinessLogicException(
                "Você atingiu o limite de plantões cadastrados.", "LIMITE_PLANTOES"
            )

        if any(m.data_marcada == dados.data for m in meus_dias):
            raise BusinessLogicException(
                "Você já marcou plantão neste dia!", "DIA_JA_MARCADO"
            )

        self.repository.create_marcacao(dados.data, user.id, unidade_id)
        self._auditar(
            registro,
            "inscrever",
            user.id,
            {"dia": dados.data, "fora_do_prazo": not self._esta_aberto()},
        )
        logger.info(
            f"Usuário {user.id} marcou plantão em {dados.data} na unidade {unidade_id}"
        )
        return self.get_pagina(user)

    @transacao_escala
    def limpar_marcacoes(self, user: UserInfo) -> dict[str, Any]:
        """Apaga todas as marcações ativas da pessoa (botão "Editar")."""
        registro = self._selecionar(lock=True)
        if not self._pode_alterar(registro, user):
            raise BusinessLogicException(
                "As inscrições desta escala não estão abertas.", "PLANTAO_FECHADO"
            )
        total = self.repository.desativar_marcacoes_do_usuario(user.id, self._unidade())
        self._auditar(
            registro,
            "retirar_inscricoes",
            user.id,
            {"quantidade": total, "fora_do_prazo": not self._esta_aberto()},
        )
        logger.info(f"Usuário {user.id} apagou {total} marcações de plantão")
        return self.get_pagina(user)

    # --- configuração (admin) ---------------------------------------------

    def get_configuracao(self) -> dict[str, Any]:
        self._selecionar()
        unidade_id = self._unidade()
        registro = self.repository.get_plantao(unidade_id=unidade_id)
        return {
            "id": registro.id if registro else None,
            "nome": registro.nome if registro else "",
            "legado": registro.legado if registro else False,
            "cancelado": registro.cancelado if registro else False,
            "data_abertura": registro.data_abertura.isoformat()
            if registro and registro.data_abertura
            else None,
            "data_fechamento": registro.data_fechamento.isoformat()
            if registro and registro.data_fechamento
            else None,
            "dias": [
                dia.data.isoformat()
                for dia in self.repository.list_dias(unidade_id=unidade_id)
                if dia.data
            ],
        }

    @transacao_escala
    def salvar_configuracao(
        self, dados: ConfiguracaoPlantaoInput, executor_id=None, criar=False
    ):
        unidade_id = self._unidade()
        # Serialize period creation/configuration per unit; marking locks the
        # period row, so quotas and duplicate checks share a transaction.
        from sqlalchemy import select

        from gestaolegal.database.tables import unidades

        self.repository.session.execute(
            select(unidades.c.id).where(unidades.c.id == unidade_id).with_for_update()
        )
        registro = None if criar else self._selecionar(lock=True)
        if registro and (registro.legado or registro.cancelado):
            raise ValidationException(
                "Escalas de legado ou canceladas são somente para consulta."
            )
        if criar and not dados.dias:
            raise ValidationException(
                "Selecione ao menos um dia de plantão.", field="dias"
            )
        antes = self.get_configuracao() if registro else None
        if not registro:
            ident = self.repository.create_plantao(
                {"unidade_id": unidade_id, "nome": dados.nome}
            )
            self.repository.escala_id = ident
            registro = self.repository.get_plantao(unidade_id=unidade_id, lock=True)
        self.repository.incluir_inativos = False
        atuais = {
            dia.data: dia for dia in self.repository.list_dias(unidade_id=unidade_id)
        }
        desejados = set(dados.dias)
        marcados = self.repository.list_marcacoes_ativas(
            unidade_id=unidade_id, todos_usuarios=True
        )
        if any(m["data_marcada"] not in desejados for m in marcados):
            raise ValidationException(
                "Não é possível retirar um dia com inscrições. Preserve o dia ou cancele a escala.",
                field="dias",
            )
        for data in desejados - set(atuais):
            existente = self.repository.find_dia_por_data(data, unidade_id=unidade_id)
            if existente:
                self.repository.set_status_dia(existente.id, True)
            else:
                self.repository.create_dia(data, unidade_id)
        for data, dia in atuais.items():
            if data not in desejados:
                self.repository.set_status_dia(dia.id, False)
        self.repository.update_plantao(
            registro.id,
            {
                "nome": dados.nome,
                "data_abertura": dados.data_abertura,
                "data_fechamento": dados.data_fechamento,
            },
        )
        self._auditar(
            registro,
            "criar" if antes is None else "configurar",
            executor_id,
            {"antes": antes, "depois": dados.model_dump(mode="json")},
        )
        if executor_id is not None and (
            antes is None or antes["data_abertura"] != dados.data_abertura.isoformat()
        ):
            from gestaolegal.database.tables import usuarios, usuarios_unidades

            destinatarios = (
                self.repository.session.execute(
                    select(usuarios.c.id)
                    .join(
                        usuarios_unidades,
                        usuarios_unidades.c.usuario_id == usuarios.c.id,
                    )
                    .where(
                        usuarios_unidades.c.unidade_id == unidade_id,
                        usuarios.c.status.is_(True),
                        usuarios.c.urole.in_(("orient", "estag_direito")),
                    )
                )
                .scalars()
                .all()
            )
            NotificacaoService().notificar(
                "plantao",
                "Prazo de inscrição da escala",
                executor_id,
                destinatarios=destinatarios,
                detalhe=f"{dados.nome}: {dados.data_abertura:%d/%m/%Y %H:%M} a {dados.data_fechamento:%d/%m/%Y %H:%M} (Brasília)",
            )
        return self.get_configuracao()
