import logging
from datetime import date
from typing import Any

from gestaolegal.exceptions import BusinessLogicException, ValidationException
from gestaolegal.models.plantao import (
    LIMITE_MARCACOES,
    LIMITE_MARCACOES_POR_UROLE,
    UROLES_IGNORAM_JANELA,
    VAGAS_POR_UROLE,
)
from gestaolegal.models.plantao_input import ConfiguracaoPlantaoInput, MarcarDiaInput
from gestaolegal.models.user import UserInfo
from gestaolegal.repositories.plantao_repository import PlantaoRepository
from gestaolegal.utils.tempo import agora_brasilia

logger = logging.getLogger(__name__)


class PlantaoService:
    repository: PlantaoRepository

    def __init__(self):
        self.repository = PlantaoRepository()

    # --- janela de marcação ----------------------------------------------

    def _encerrar_se_expirado(self) -> None:
        """Encerra o plantão quando a data de fechamento já passou.

        A v2 fazia isso como efeito colateral do carregamento da página; aqui é
        um passo idempotente chamado no início das operações de leitura e
        escrita. Diferente da v2, os dias são desativados (`status=False`) em vez
        de apagados fisicamente, preservando o histórico das marcações.
        """
        registro = self.repository.get_plantao()
        if not registro or not registro.data_fechamento:
            return
        if registro.data_fechamento >= agora_brasilia():
            return

        logger.info(
            f"Plantão encerrado em {registro.data_fechamento}; "
            "desativando dias e marcações"
        )
        self.repository.desativar_todos_dias()
        self.repository.desativar_todas_marcacoes()
        self.repository.update_plantao(
            registro.id, {"data_abertura": None, "data_fechamento": None}
        )

    def _esta_aberto(self) -> bool:
        registro = self.repository.get_plantao()
        if not registro or not registro.data_abertura:
            return False
        if registro.data_fechamento and registro.data_fechamento < agora_brasilia():
            return False
        return True

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

        todos_lotados = bool(dias) and all(
            ocupacao[dia] >= limite for dia in dias
        )
        if todos_lotados:
            return {dia: limite for dia in dias}

        return {dia: max(limite - ocupacao[dia], 0) for dia in dias}

    # --- leitura -----------------------------------------------------------

    def get_pagina(self, user: UserInfo) -> dict[str, Any]:
        """Tudo que a tela da escala precisa, em uma resposta só."""
        self._encerrar_se_expirado()

        registro = self.repository.get_plantao()
        aberto = self._esta_aberto()
        dias = [dia.data for dia in self.repository.list_dias()]
        marcacoes = self.repository.list_marcacoes_ativas()
        vagas = self._vagas_por_dia(dias, marcacoes, user.urole)

        meus_dias = self.repository.list_marcacoes_ativas_do_usuario(user.id)

        return {
            "plantao": {
                "data_abertura": registro.data_abertura if registro else None,
                "data_fechamento": registro.data_fechamento if registro else None,
                "aberto": aberto,
            },
            "pode_marcar": aberto or user.urole in UROLES_IGNORAM_JANELA,
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
                    "data": m["data_marcada"].isoformat(),
                    "id_usuario": m["id_usuario"],
                    "nome": m["nome"],
                    "urole": m["urole"],
                }
                for m in marcacoes
            ],
            "meus_dias": [
                {
                    "id": m.id,
                    "data_marcada": m.data_marcada.isoformat(),
                    "confirmacao": m.confirmacao,
                }
                for m in meus_dias
            ],
        }

    # --- marcação ----------------------------------------------------------

    def marcar_dia(self, dados: MarcarDiaInput, user: UserInfo) -> dict[str, Any]:
        self._encerrar_se_expirado()

        if not self._esta_aberto() and user.urole not in UROLES_IGNORAM_JANELA:
            raise BusinessLogicException(
                "O plantão não está aberto!", "PLANTAO_FECHADO"
            )

        dias = [dia.data for dia in self.repository.list_dias()]
        if dados.data not in dias:
            raise ValidationException(
                "Data selecionada não foi aberta para plantão.", field="data"
            )

        marcacoes = self.repository.list_marcacoes_ativas()
        vagas = self._vagas_por_dia(dias, marcacoes, user.urole)
        restantes = vagas[dados.data]
        if restantes is not None and restantes <= 0:
            raise BusinessLogicException(
                "Não há vagas disponíveis na data selecionada, tente outro dia.",
                "SEM_VAGAS",
            )

        meus_dias = self.repository.list_marcacoes_ativas_do_usuario(user.id)
        if len(meus_dias) >= self._limite_marcacoes(user.urole):
            raise BusinessLogicException(
                "Você atingiu o limite de plantões cadastrados.", "LIMITE_PLANTOES"
            )

        if any(m.data_marcada == dados.data for m in meus_dias):
            raise BusinessLogicException(
                "Você já marcou plantão neste dia!", "DIA_JA_MARCADO"
            )

        self.repository.create_marcacao(dados.data, user.id)
        logger.info(f"Usuário {user.id} marcou plantão em {dados.data}")
        return self.get_pagina(user)

    def limpar_marcacoes(self, user: UserInfo) -> dict[str, Any]:
        """Apaga todas as marcações ativas da pessoa (botão "Editar")."""
        self._encerrar_se_expirado()
        total = self.repository.desativar_marcacoes_do_usuario(user.id)
        logger.info(f"Usuário {user.id} apagou {total} marcações de plantão")
        return self.get_pagina(user)

    # --- configuração (admin) ---------------------------------------------

    def get_configuracao(self) -> dict[str, Any]:
        registro = self.repository.get_plantao()
        return {
            "data_abertura": registro.data_abertura if registro else None,
            "data_fechamento": registro.data_fechamento if registro else None,
            "dias": [dia.data.isoformat() for dia in self.repository.list_dias()],
        }

    def salvar_configuracao(self, dados: ConfiguracaoPlantaoInput) -> dict[str, Any]:
        """Salva a janela e faz o diff dos dias abertos.

        Dias retirados são desativados em vez de apagados: a v2 fazia DELETE
        físico, deixando marcações órfãs apontando para datas inexistentes.
        """
        atuais = {dia.data: dia for dia in self.repository.list_dias()}
        desejados = set(dados.dias)

        for data in desejados - set(atuais):
            existente = self.repository.find_dia_por_data(data)
            if existente:
                # Dia que já foi aberto antes e estava desativado: reativa.
                self.repository.set_status_dia(existente.id, True)
            else:
                self.repository.create_dia(data)

        for data, dia in atuais.items():
            if data not in desejados:
                self.repository.set_status_dia(dia.id, False)

        janela = {
            "data_abertura": dados.data_abertura,
            "data_fechamento": dados.data_fechamento,
        }
        registro = self.repository.get_plantao()
        if registro:
            self.repository.update_plantao(registro.id, janela)
        else:
            self.repository.create_plantao(janela)

        logger.info(
            f"Configuração do plantão salva: {len(desejados)} dias, "
            f"janela {dados.data_abertura} → {dados.data_fechamento}"
        )
        return self.get_configuracao()
