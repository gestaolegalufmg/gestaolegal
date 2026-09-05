from dataclasses import asdict

from flask import Blueprint, request, send_file

from gestaolegal.common import PageParams
from gestaolegal.services.arquivo_service import ArquivoService
from gestaolegal.services.private_file_storage import aplicar_headers_download
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext

arquivo_controller = Blueprint("arquivo", __name__)

# Mesmas regras da v2: todos veem e baixam; admin, professor e colaboradores
# cadastram/editam; colaborador externo não exclui.
PAPEIS_EDITAM = ("admin", "prof", "colab_proj", "colab_ext")
PAPEIS_EXCLUEM = ("admin", "prof", "colab_proj")


@arquivo_controller.route("/", methods=["GET"])
@authenticated
def listar():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    result = ArquivoService().search(
        PageParams(page=page, per_page=per_page), search=search
    )
    return success_response(data=result.to_dict())


@arquivo_controller.route("/<int:id>", methods=["GET"])
@authenticated
def buscar(id: int):
    return success_response(data=asdict(ArquivoService().find_by_id(id)))


@arquivo_controller.route("/", methods=["POST"])
@authorized(*PAPEIS_EDITAM)
def criar():
    user = RequestContext.get_current_user()
    arquivo = ArquivoService().create(
        titulo=request.form.get("titulo", ""),
        descricao=request.form.get("descricao"),
        file=request.files.get("arquivo"),
        criado_por=user.id,
    )
    return success_response(
        data=asdict(arquivo), message="Arquivo adicionado", status_code=201
    )


@arquivo_controller.route("/<int:id>", methods=["PUT"])
@authorized(*PAPEIS_EDITAM)
def editar(id: int):
    arquivo = ArquivoService().update(
        id,
        titulo=request.form.get("titulo", ""),
        descricao=request.form.get("descricao"),
        file=request.files.get("arquivo"),
    )
    return success_response(data=asdict(arquivo), message="Arquivo editado")


@arquivo_controller.route("/<int:id>", methods=["DELETE"])
@authorized(*PAPEIS_EXCLUEM)
def excluir(id: int):
    ArquivoService().delete(id)
    return success_response(message="Arquivo excluído")


@arquivo_controller.route("/<int:id>/download", methods=["GET"])
@authenticated
def download(id: int):
    caminho, nome = ArquivoService().get_for_download(id)
    return aplicar_headers_download(
        send_file(caminho, as_attachment=True, download_name=nome)
    )
