import logging
import os
from datetime import datetime
from typing import Optional

from flask import current_app
from werkzeug.exceptions import RequestEntityTooLarge

from gestaolegal.common.constants import tipo_evento
from gestaolegal.models.evento import Evento
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.repositories.evento_repository import EventoRepository
from gestaolegal.schemas.arquivos_evento import ArquivosEventoSchema
from gestaolegal.services.arquivo_service import ArquivoService

opcoes_filtro_eventos = tipo_evento.copy()
opcoes_filtro_eventos["TODOS"] = ("todos", "Todos")

logger = logging.getLogger(__name__)


class EventoService:
    def __init__(self):
        self.repository = EventoRepository()
        self.arquivo_service = ArquivoService()

    def get_num_eventos_atual(self, caso_id):
        """Get the next event number for a case"""
        return self.repository.get_next_event_number(caso_id)

    def create_evento(
        self,
        caso_id: int,
        tipo: str,
        descricao: str,
        data_evento: datetime,
        id_criado_por: int,
        id_usuario_responsavel: Optional[int] = None,
    ) -> Evento:
        evento_data = {
            "id_caso": caso_id,
            "num_evento": self.get_num_eventos_atual(caso_id),
            "tipo": tipo,
            "descricao": descricao,
            "data_evento": data_evento,
            "data_criacao": datetime.now(),
            "id_criado_por": id_criado_por,
            "id_usuario_responsavel": id_usuario_responsavel,
        }

        return self.repository.create(evento_data)

    def get_eventos_by_caso(
        self, caso_id: int, opcao_filtro: str, page_params: PageParams
    ):
        """Get events for a case with filter options"""
        return self.repository.get_eventos_by_caso_with_filter(
            caso_id, opcao_filtro, page_params
        )

    def get_evento_by_id(self, evento_id: int) -> Optional[Evento]:
        return self.repository.find_by_id(evento_id)

    def get_evento_by_numero(self, num_evento: int, caso_id: int) -> Optional[Evento]:
        return self.repository.get_evento_by_numero(num_evento, caso_id)

    def get_evento_with_arquivos(
        self, num_evento: int, caso_id: int
    ) -> tuple[Optional[Evento], list[ArquivosEventoSchema]]:
        evento = self.get_evento_by_numero(num_evento, caso_id)
        if not evento:
            return None, []

        arquivos = self.get_arquivos_by_evento(evento.id)
        return evento, arquivos

    def update_evento(
        self,
        evento_id: int,
        tipo: str,
        descricao: str,
        data_evento: datetime,
        id_usuario_responsavel: Optional[int] = None,
    ) -> Evento:
        evento = self.repository.find_by_id(evento_id)
        if not evento:
            raise ValueError("Evento não encontrado")

        update_data = {
            "tipo": tipo,
            "descricao": descricao,
            "data_evento": data_evento,
            "id_usuario_responsavel": id_usuario_responsavel,
        }
        return self.repository.update(evento_id, update_data)

    def delete_evento(self, evento_id: int) -> None:
        evento = self.repository.find_by_id(evento_id)
        if not evento:
            raise ValueError("Evento não encontrado")

        # Handle file deletion if needed
        if hasattr(evento, "arquivo") and evento.arquivo:
            local_arquivo = os.path.join(
                current_app.root_path,
                "static",
                "eventos",
                f"evento_{evento.id}_{evento.arquivo}",
            )
            if os.path.exists(local_arquivo):
                os.remove(local_arquivo)

        self.repository.delete(evento_id)

    def get_arquivos_by_evento(self, evento_id: int) -> list[ArquivosEventoSchema]:
        return self.arquivo_service.get_arquivos_by_evento(evento_id)

    def create_arquivo_evento(
        self, caso_id: int, evento_id: int, link_arquivo: str
    ) -> ArquivosEventoSchema:
        return self.arquivo_service.create_arquivo_evento(
            caso_id, evento_id, link_arquivo
        )

    def update_evento_with_files(
        self,
        evento_id: int,
        tipo: str,
        descricao: str,
        data_evento: datetime,
        id_usuario_responsavel: Optional[int] = None,
        arquivos: Optional[list] = None,
    ) -> Evento:
        evento = self.update_evento(
            evento_id=evento_id,
            tipo=tipo,
            descricao=descricao,
            data_evento=data_evento,
            id_usuario_responsavel=id_usuario_responsavel,
        )

        if arquivos:
            for arquivo in arquivos:
                if arquivo and arquivo.filename:
                    try:
                        nome_arquivo = self.save_arquivo(arquivo)
                        self.create_arquivo_evento(
                            evento.id_caso, evento_id, nome_arquivo
                        )
                    except ValueError as e:
                        logger.warning(f"Error saving arquivo: {str(e)}")
                        continue
                    except RequestEntityTooLarge:
                        logger.warning("File too large")
                        continue

        return evento

    def save_arquivo(self, arquivo) -> str:
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

    def params_busca_eventos(self, eventos, rota_paginacao, caso_id, opcao_filtro=None):
        """Build parameters for event search"""
        return {
            "eventos": eventos,
            "rota_paginacao": rota_paginacao,
            "opcao_filtro": opcao_filtro,
            "caso_id": caso_id,
        }
