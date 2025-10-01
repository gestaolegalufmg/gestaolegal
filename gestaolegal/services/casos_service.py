import logging
import os
from datetime import datetime
from typing import Optional

import pytz
from flask import current_app

from gestaolegal.common import PageParams
from gestaolegal.common.constants import UserRole, situacao_deferimento
from gestaolegal.common.constants.atendido import TipoBusca
from gestaolegal.models.caso import Caso
from gestaolegal.models.evento import Evento
from gestaolegal.models.lembrete import Lembrete
from gestaolegal.models.roteiro import Roteiro
from gestaolegal.repositories.atendido_repository import AtendidoRepository
from gestaolegal.repositories.base_repository import WhereConditions
from gestaolegal.repositories.caso_repository import CasoRepository
from gestaolegal.repositories.roteiro_repository import RoteiroRepository
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.services.arquivo_service import ArquivoService
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.services.evento_service import EventoService
from gestaolegal.services.historico_service import HistoricoService
from gestaolegal.services.lembrete_service import LembreteService
from gestaolegal.services.notificacao_service import NotificacaoService

# Title constant
TITULO_TOTAL_MEUS_CASOS = "Total de Casos: {}"

logger = logging.getLogger(__name__)


class CasosService:
    repository: CasoRepository
    user_repository: UserRepository
    atendido_repository: AtendidoRepository
    roteiro_repository: RoteiroRepository
    evento_service: EventoService
    lembrete_service: LembreteService
    arquivo_service: ArquivoService
    notification_service: NotificacaoService
    historico_service: HistoricoService
    atendido_service: AtendidoService

    def __init__(self):
        self.repository = CasoRepository()
        self.user_repository = UserRepository()
        self.atendido_repository = AtendidoRepository()
        self.roteiro_repository = RoteiroRepository()
        self.evento_service = EventoService()
        self.lembrete_service = LembreteService()
        self.arquivo_service = ArquivoService()
        self.notification_service = NotificacaoService()
        self.historico_service = HistoricoService()
        self.atendido_service = AtendidoService()

    def find_by_id(self, caso_id: int):
        return self.repository.find_by_id(caso_id)

    def create(self, caso_data: dict) -> Caso:
        logger.info(f"Creating new case in area: {caso_data.get('area_direito')}")

        data = caso_data.copy()
        data.pop("csrf_token", None)

        area_direito = data.get("area_direito")
        sub_area = data.get("sub_area")
        sub_area_admin = data.get("sub_area_admin")

        calculated_sub_area = None
        if area_direito == "civel":
            calculated_sub_area = sub_area or ""
        elif area_direito == "administrativo":
            calculated_sub_area = sub_area_admin or ""

        data["sub_area"] = calculated_sub_area
        data["data_criacao"] = datetime.now(tz=pytz.timezone("America/Sao_Paulo"))
        data["data_modificacao"] = datetime.now(tz=pytz.timezone("America/Sao_Paulo"))

        clientes_ids = data.pop("clientes", None)

        caso = self.repository.create_with_clientes(data, clientes_ids)
        logger.info(f"Case created successfully with ID: {caso.id}")
        return caso

    def update(self, caso_id: int, caso_data: dict) -> Caso:
        data = caso_data.copy()
        data.pop("csrf_token", None)
        data.pop("submit", None)

        orientador_value = data.get("orientador")
        estagiario_value = data.get("estagiario")
        colaborador_value = data.get("colaborador")

        id_orientador = int(orientador_value) if orientador_value else None
        id_estagiario = int(estagiario_value) if estagiario_value else None
        id_colaborador = int(colaborador_value) if colaborador_value else None

        situacao = data.get("situacao_deferimento_ativo") or data.get(
            "situacao_deferimento_indeferido"
        )

        update_data = {
            "area_direito": data.get("area_direito"),
            "descricao": data.get("descricao"),
            "id_orientador": id_orientador,
            "id_estagiario": id_estagiario,
            "id_colaborador": id_colaborador,
            "data_modificacao": datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
            "id_modificado_por": data.get("id_modificado_por"),
        }

        if situacao:
            update_data["situacao_deferimento"] = situacao

        return self.repository.update(caso_id, update_data)

    def deferir_caso(self, caso_id: int) -> Caso:
        return self.repository.update(
            caso_id, {"situacao_deferimento": situacao_deferimento["ATIVO"][0]}
        )

    def indeferir_caso(self, caso_id: int, justificativa: str) -> Caso:
        return self.repository.update(
            caso_id,
            {
                "situacao_deferimento": situacao_deferimento["INDEFERIDO"][0],
                "justif_indeferimento": justificativa,
            },
        )

    def delete_caso(self, caso_id: int) -> None:
        arquivos = self.repository.get_arquivos_by_caso(caso_id)

        for arquivo in arquivos:
            if arquivo and arquivo.link_arquivo:
                local_arquivo = os.path.join(
                    current_app.root_path, "static", "casos", arquivo.link_arquivo
                )
                if os.path.exists(local_arquivo):
                    os.remove(local_arquivo)

        self.repository.delete_arquivos_by_caso(caso_id)
        self.repository.delete(caso_id)

    def add_cliente_to_caso(self, caso_id: int, cliente_id: int) -> None:
        if not self.repository.add_cliente_to_caso(caso_id, cliente_id):
            raise ValueError(
                f"Erro ao adicionar cliente {cliente_id} ao caso {caso_id}"
            )

    def remove_cliente_from_caso(self, caso_id: int, cliente_id: int) -> None:
        if not self.repository.remove_cliente_from_caso(caso_id, cliente_id):
            raise ValueError(f"Erro ao remover cliente {cliente_id} do caso {caso_id}")

    def search_casos(self, termo: str) -> list[dict]:
        where_clauses: WhereConditions = []

        if termo:
            where_clauses.append(("id", "like", f"{termo}%"))

        page_params = PageParams(page=1, per_page=5) if not termo else None

        result = self.repository.get(
            where_conditions=where_clauses, order_by=["id"], page_params=page_params
        )

        casos = result.items

        if not casos:
            return [{"id": 1, "text": "Não há casos cadastrados no sistema"}]

        return [{"id": caso.id, "text": f"Caso {caso.id}"} for caso in casos]

    def validate_lembrete_permission(
        self, lembrete_id: int, user_id: int, user_role: str
    ) -> bool:
        lembrete = self.lembrete_service.get_lembrete_by_id(lembrete_id)

        if not lembrete:
            return False

        if user_role == UserRole.ADMINISTRADOR:
            return True

        if user_id == lembrete.id_do_criador:
            return True

        return False

    def validate_evento_permission(
        self, evento_id: int, user_id: int, user_role: str
    ) -> bool:
        evento = self.evento_service.find_by_id(evento_id)

        if not evento:
            return False

        if user_role == UserRole.ADMINISTRADOR:
            return True

        if user_id == evento.id_criado_por:
            return True

        return False

    def save_arquivo(
        self, arquivo, caso_id: Optional[int] = None, evento_id: Optional[int] = None
    ) -> str:
        if not arquivo or not arquivo.filename:
            raise ValueError("Nenhum arquivo fornecido")

        _, extensao_do_arquivo = os.path.splitext(arquivo.filename)
        if extensao_do_arquivo != ".pdf":
            raise ValueError(
                "Extensão de arquivo não suportado. Apenas PDFs são aceitos."
            )

        nome_arquivo = arquivo.filename
        arquivo.save(
            os.path.join(current_app.root_path, "static", "casos", nome_arquivo)
        )

        return nome_arquivo

    def validate_caso_edit_permission(
        self, caso: Caso, user_id: int, user_role: str
    ) -> tuple[bool, str]:
        if user_role == UserRole.COLAB_EXTERNO and caso.id_colaborador != user_id:
            return False, "Você não tem permissão para editar esse caso."

        if user_role == UserRole.ESTAGIARIO_DIREITO and caso.id_estagiario != user_id:
            return False, "Você não tem permissão para editar esse caso."

        return True, ""

    def params_busca_casos(self, casos, rota_paginacao, opcao_filtro=None):
        return {
            "casos": casos,
            "rota_paginacao": rota_paginacao,
            "opcao_filtro": opcao_filtro,
        }

    def titulo_total_meus_casos(self, numero_casos):
        return TITULO_TOTAL_MEUS_CASOS.format(numero_casos)

    def adicionar_assistidos_ao_caso(self, caso_id: int, form_data) -> None:
        assistidos_ids = form_data.get("assistidos", "").split(",")
        for assistido_id in assistidos_ids:
            if assistido_id.strip():
                self.add_cliente_to_caso(caso_id, int(assistido_id.strip()))

    def create_lembrete_with_notification(
        self, form, caso_id: int, current_user_id: int
    ) -> Lembrete:
        lembrete_data = form.to_dict()
        lembrete_data["id_caso"] = caso_id
        lembrete_data["id_do_criador"] = current_user_id

        lembrete = self.lembrete_service.create_lembrete(
            caso_id=caso_id,
            id_usuario=lembrete_data["id_usuario"],
            data_lembrete=lembrete_data["data_lembrete"],
            descricao=lembrete_data["descricao"],
            id_do_criador=current_user_id,
        )

        return lembrete

    def update_lembrete(self, id_lembrete: int, form) -> Lembrete:
        lembrete_data = form.to_dict()
        return self.lembrete_service.update_lembrete(
            lembrete_id=id_lembrete,
            id_usuario=lembrete_data["id_usuario"],
            data_lembrete=lembrete_data["data_lembrete"],
            descricao=lembrete_data["descricao"],
        )

    def get_editar_lembrete_data(self, lembrete_id: int) -> dict:
        lembrete = self.lembrete_service.get_lembrete_by_id(lembrete_id)
        if not lembrete:
            return {}

        return {"form": lembrete.to_dict(), "lembrete": lembrete}

    def create_evento_with_files_and_notification(
        self, form, caso_id: int, current_user_id: int, request
    ) -> Evento:
        evento_data = form.to_dict()
        evento_data["id_caso"] = caso_id
        evento_data["id_criado_por"] = current_user_id

        evento = self.evento_service.create_evento(
            caso_id=caso_id,
            tipo=evento_data["tipo"],
            descricao=evento_data["descricao"],
            data_evento=evento_data["data_evento"],
            id_criado_por=current_user_id,
            id_usuario_responsavel=evento_data.get("id_usuario_responsavel"),
        )

        return evento

    def update_evento_with_files(self, evento_id: int, form, request) -> Evento:
        evento_data = form.to_dict()

        evento = self.evento_service.update_evento_with_files(
            evento_id=evento_id,
            tipo=evento_data["tipo"],
            descricao=evento_data["descricao"],
            data_evento=evento_data["data_evento"],
            id_usuario_responsavel=evento_data.get("id_usuario_responsavel"),
            arquivos=request.files.getlist("arquivos")
            if hasattr(request, "files")
            else None,
        )

        return evento

    def get_editar_evento_data(self, evento_id: int) -> dict:
        evento = self.evento_service.find_by_id(evento_id)
        if not evento:
            raise ValueError(f"Evento with id {evento_id} not found")

        return {"form": evento.to_dict(), "evento": evento}

    def get_eventos_by_caso(
        self, caso_id: int, opcao_filtro: str, page_params: PageParams
    ):
        return self.evento_service.get_eventos_by_caso(
            caso_id, opcao_filtro, page_params
        )

    def delete_evento(self, evento_id: int) -> None:
        return self.evento_service.delete_evento(evento_id)

    def params_busca_eventos(self, eventos, rota_paginacao, caso_id, opcao_filtro=None):
        return self.evento_service.params_busca_eventos(
            eventos, rota_paginacao, caso_id, opcao_filtro
        )

    def update_arquivo_caso(self, id_arquivo: int, request) -> None:
        arquivo_data = request.form.to_dict()
        self.arquivo_service.update_arquivo_caso(id_arquivo, arquivo_data)

    def update_arquivo_evento(self, id_arquivo: int, request) -> None:
        arquivo_data = request.form.to_dict()
        self.arquivo_service.update_arquivo_evento(id_arquivo, arquivo_data)

    def get_arquivos_by_caso(self, caso_id: int):
        return self.repository.get_arquivos_by_caso(caso_id)

    def get_casos_with_filters(self, opcao_filtro: str, page_params: PageParams):
        return self.repository.get_casos_with_filters(opcao_filtro, page_params)

    def get_meus_casos(self, user_id: int, opcao_filtro: str, page_params: PageParams):
        return self.repository.get_meus_casos(user_id, opcao_filtro, page_params)

    def create_or_update_roteiro(self, area_direito: str, link: str) -> Roteiro:
        roteiro = self.roteiro_repository.find_by_area_direito(area_direito)

        if roteiro:
            return self.roteiro_repository.update(roteiro.id, {"link": link})

        return self.roteiro_repository.create(
            {"area_direito": area_direito, "link": link}
        )

    def get_all_roteiros(self):
        return self.roteiro_repository.get()
