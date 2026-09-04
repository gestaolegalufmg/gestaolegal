import logging
from datetime import date, datetime, time
from typing import Any

from gestaolegal.exceptions import NotFoundException
from gestaolegal.models.plantao import Confirmacao
from gestaolegal.models.presenca import StatusPresenca
from gestaolegal.models.presenca_input import (
    ConfirmacaoBatchInput,
    RegistrarPresencaInput,
)
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.plantao_repository import PlantaoRepository
from gestaolegal.repositories.presenca_repository import PresencaRepository
from gestaolegal.utils.request_context import RequestContext
from gestaolegal.utils.tempo import agora_brasilia, dia_util_anterior, hoje_brasilia

logger = logging.getLogger(__name__)


class PresencaService:
    repository: PresencaRepository
    plantao_repository: PlantaoRepository

    def __init__(self):
        self.repository = PresencaRepository()
        # A tela de conferência confere presenças e dias de plantão lado a lado.
        self.plantao_repository = PlantaoRepository()

    def _unidade(self) -> int:
        return RequestContext.get_unidade_ativa()

    # --- relógio de ponto --------------------------------------------------

    def _fechar_registros_vencidos(self, id_usuario: int) -> None:
        """Fecha um registro que ficou em aberto de um dia anterior.

        A v2 comparava dia, mês e ano em campos separados, o que deixava passar
        registros da virada de mês ou de ano.
        """
        aberto = self.repository.find_aberto_do_usuario(
            id_usuario, unidade_id=self._unidade()
        )
        if not aberto or aberto.data_entrada.date() >= hoje_brasilia():
            return

        logger.info(
            f"Fechando registro {aberto.id} do usuário {id_usuario}, "
            f"aberto desde {aberto.data_entrada}"
        )
        self.repository.update(aberto.id, {"status": False})

    def get_estado(self, user: UserInfo) -> dict[str, Any]:
        self._fechar_registros_vencidos(user.id)

        aberto = self.repository.find_aberto_do_usuario(
            user.id, unidade_id=self._unidade()
        )
        agora = agora_brasilia()

        return {
            "status_presenca": (
                StatusPresenca.SAIDA if aberto else StatusPresenca.ENTRADA
            ),
            "registro_aberto": (
                {"id": aberto.id, "data_entrada": aberto.data_entrada}
                if aberto
                else None
            ),
            "data_hoje": agora.date().isoformat(),
            "hora_sugerida": agora.strftime("%H:%M"),
        }

    def registrar(
        self, dados: RegistrarPresencaInput, user: UserInfo
    ) -> dict[str, Any]:
        self._fechar_registros_vencidos(user.id)

        horas, minutos = (int(parte) for parte in dados.hora.split(":"))
        momento = datetime.combine(hoje_brasilia(), time(horas, minutos))

        aberto = self.repository.find_aberto_do_usuario(
            user.id, unidade_id=self._unidade()
        )
        if aberto:
            self.repository.update(
                aberto.id, {"data_saida": momento, "status": False}
            )
            acao = StatusPresenca.SAIDA
            logger.info(f"Saída registrada para o usuário {user.id} às {momento}")
        else:
            self.repository.create(
                {
                    "data_entrada": momento,
                    # Provisório até a saída ser registrada (coluna NOT NULL).
                    "data_saida": datetime.combine(momento.date(), time(23, 59, 59)),
                    "id_usuario": user.id,
                    "status": True,
                    "confirmacao": Confirmacao.ABERTO,
                    "unidade_id": self._unidade(),
                }
            )
            acao = StatusPresenca.ENTRADA
            logger.info(f"Entrada registrada para o usuário {user.id} às {momento}")

        return {"acao": acao, **self.get_estado(user)}

    # --- conferência -------------------------------------------------------

    def listar_para_confirmacao(self, dia: date | None = None) -> dict[str, Any]:
        dia = dia or dia_util_anterior()

        presencas = [
            {
                "id": p["id"],
                "id_usuario": p["id_usuario"],
                "nome": p["nome"],
                "urole": p["urole"],
                "data_entrada": p["data_entrada"],
                "data_saida": p["data_saida"],
                "confirmacao": p["confirmacao"],
            }
            for p in self.repository.list_para_confirmacao(
                dia, unidade_id=self._unidade()
            )
        ]

        plantoes = [
            {
                "id": m["id"],
                "id_usuario": m["id_usuario"],
                "nome": m["nome"],
                "urole": m["urole"],
                "data_marcada": m["data_marcada"].isoformat(),
                "confirmacao": m["confirmacao"],
            }
            for m in self.plantao_repository.list_marcacoes_para_confirmacao(
                dia, unidade_id=self._unidade()
            )
        ]

        return {"data": dia.isoformat(), "presencas": presencas, "plantoes": plantoes}

    def confirmar_em_lote(self, dados: ConfirmacaoBatchInput) -> dict[str, int]:
        for item in dados.presencas:
            if not self.repository.find_by_id(item.id, unidade_id=self._unidade()):
                raise NotFoundException(resource="RegistroEntrada", resource_id=item.id)
            self.repository.update_confirmacao(item.id, item.confirmacao)

        for item in dados.plantoes:
            if not self.plantao_repository.find_marcacao_by_id(
                item.id, unidade_id=self._unidade()
            ):
                raise NotFoundException(
                    resource="DiaMarcadoPlantao", resource_id=item.id
                )
            self.plantao_repository.update_confirmacao_marcacao(
                item.id, item.confirmacao
            )

        logger.info(
            f"Conferência salva: {len(dados.presencas)} presenças, "
            f"{len(dados.plantoes)} plantões"
        )
        return {
            "presencas_atualizadas": len(dados.presencas),
            "plantoes_atualizados": len(dados.plantoes),
        }
