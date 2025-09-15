import logging
import os

from flask import current_app
from werkzeug.datastructures import FileStorage

from gestaolegal.models.arquivo import Arquivo
from gestaolegal.models.arquivo_caso import ArquivoCaso
from gestaolegal.models.arquivos_evento import ArquivosEvento
from gestaolegal.repositories.arquivo_repository import ArquivoRepository
from gestaolegal.common import PageParams
from gestaolegal.schemas.arquivo import ArquivoSchema

logger = logging.getLogger(__name__)


class ArquivoService:
    def __init__(self):
        self.repository = ArquivoRepository()

    def get(self, search: str | None, page_params: PageParams) -> list[Arquivo]:
        where_clauses = []

        if search:
            where_clauses.append(ArquivoSchema.titulo.ilike(f"%{search}%"))

        result = self.repository.get_all(
            where_clauses=where_clauses, page_params=page_params
        )

        logger.info(f"Result: {result.items}")

        return result

    def find_by_id(self, id: int) -> Arquivo | None:
        arquivo = self.repository.find_by_id(id)
        if not arquivo:
            return None
        blob = open(
            os.path.join(current_app.root_path, "static", "arquivos", arquivo.nome),
            "rb",
        ).read()

        arquivo_data = arquivo.to_dict()
        arquivo_data["blob"] = blob
        return Arquivo(**arquivo_data)

    def find_arquivo_caso_by_id(self, id: int) -> ArquivoCaso | None:
        return self.repository.find_arquivo_caso_by_id(id)

    def find_arquivo_evento_by_id(self, id: int) -> ArquivosEvento | None:
        return self.repository.find_arquivo_evento_by_id(id)

    def delete(self, id: int) -> None:
        arquivo = self.repository.find_by_id(id)

        self.__delete_arquivo_file(arquivo.nome)
        self.repository.delete(id)

    def create(self, arquivo_data: dict, arquivo_blob: FileStorage) -> Arquivo:
        logger.info(f"Creating arquivo with data: {arquivo_data}")
        logger.info(f"Creating arquivo with blob: {arquivo_blob}")
        if not arquivo_blob:
            raise ValueError("Arquivo não fornecido")

        arquivo_data.pop("csrf_token")
        arquivo_data.pop("arquivo")

        arquivo_data["nome"] = arquivo_blob.filename

        self.__save_file_on_filesystem(arquivo_blob)

        return self.repository.create(arquivo_data)

    def create_arquivo_caso(self, caso_id: int, link_arquivo: str) -> ArquivoCaso:
        arquivo_data = {
            "link_arquivo": link_arquivo,
            "id_caso": caso_id,
        }
        return self.repository.create_arquivo_caso(arquivo_data)

    def create_arquivo_evento(
        self, caso_id: int, evento_id: int, link_arquivo: str
    ) -> ArquivosEvento:
        arquivo_data = {
            "link_arquivo": link_arquivo,
            "id_caso": caso_id,
            "id_evento": evento_id,
        }
        return self.repository.create_arquivo_evento(arquivo_data)

    def get_arquivos_by_caso(self, caso_id: int) -> list[ArquivoCaso]:
        return self.repository.get_arquivos_by_caso(caso_id)

    def get_arquivos_by_evento(self, evento_id: int) -> list[ArquivosEvento]:
        return self.repository.get_arquivos_by_evento(evento_id)

    def delete_arquivo_caso(self, arquivo_id: int) -> None:
        if not self.repository.delete_arquivo_caso(arquivo_id):
            raise ValueError("Arquivo não encontrado")

    def delete_arquivo_evento(self, arquivo_id: int) -> None:
        if not self.repository.delete_arquivo_evento(arquivo_id):
            raise ValueError("Arquivo não encontrado")

    def update_arquivo_caso(self, arquivo_id: int, link_arquivo: str) -> ArquivoCaso:
        arquivo = self.repository.update_arquivo_caso(
            arquivo_id, {"link_arquivo": link_arquivo}
        )
        if not arquivo:
            raise ValueError("Arquivo não encontrado")
        return arquivo

    def update_arquivo_evento(
        self, arquivo_id: int, link_arquivo: str
    ) -> ArquivosEvento:
        arquivo = self.repository.update_arquivo_evento(
            arquivo_id, {"link_arquivo": link_arquivo}
        )
        if not arquivo:
            raise ValueError("Arquivo não encontrado")
        return arquivo

    def __save_file_on_filesystem(self, arquivo: FileStorage) -> None:
        if not arquivo or not arquivo.filename:
            raise ValueError("Nenhum arquivo fornecido")

        path = os.path.join(
            current_app.root_path, "static", "arquivos", arquivo.filename
        )
        logger.info(f"Salvando arquivo em: {path}")

        arquivo.save(path)

        logger.info(f"Arquivo salvo em: {path}")

    def update(self, id: int, form: dict, request) -> dict:
        try:
            arquivo = self.repository.find_by_id(id)

            form_data = dict(form)
            form_data.pop("csrf_token", None)

            if "arquivo" in request.files and request.files["arquivo"].filename:
                new_file = request.files["arquivo"]
                old_filename = arquivo.nome

                form_data["nome"] = new_file.filename
                self.__save_file_on_filesystem(new_file)

                old_file_path = os.path.join(
                    current_app.root_path, "static", "arquivos", old_filename
                )
                if os.path.exists(old_file_path) and old_filename != new_file.filename:
                    os.remove(old_file_path)
            else:
                form_data.pop("nome", None)

            form_data.pop("arquivo", None)

            updated_arquivo = self.repository.update(id, form_data)

            return updated_arquivo
        except Exception as e:
            logger.error(f"Error updating arquivo {id}: {str(e)}", exc_info=True)
            raise e

    def __delete_arquivo_file(self, filename: str) -> None:
        local_arquivo = os.path.join(current_app.root_path, "static", "casos", filename)
        if os.path.exists(local_arquivo):
            os.remove(local_arquivo)
