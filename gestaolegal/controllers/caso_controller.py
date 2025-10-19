import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, cast

from dateutil import parser
from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams
from gestaolegal.config import Config
from gestaolegal.exceptions import (
    FileOperationException,
    NotFoundException,
    ValidationException,
)
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.models.user import UserInfo
from gestaolegal.services.caso_service import CasoService
from gestaolegal.services.evento_service import EventoService
from gestaolegal.services.processo_service import ProcessoService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response
from gestaolegal.utils.request_context import RequestContext
from gestaolegal.utils.StringBool import StringBool

caso_controller = Blueprint("caso_api", __name__)


@caso_controller.route("/", methods=["GET"])
@authenticated
def get():
    current_user: UserInfo = RequestContext.get_current_user()
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )
    situacao_deferimento = request.args.get(
        "situacao_deferimento", default=None, type=str
    )
    user = request.args.get("user", default=None, type=str)

    id_usuario_responsavel = None
    if user == "me":
        id_usuario_responsavel = current_user.id
    elif user is not None and user.isdigit():
        id_usuario_responsavel = int(user)

    caso_service = CasoService()
    result = caso_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive.value,
        situacao_deferimento=situacao_deferimento,
        id_usuario_responsavel=id_usuario_responsavel,
    )

    return success_response(data=result.to_dict())


@caso_controller.route("/<int:id>", methods=["GET"])
@authenticated
def find_by_id(id: int):
    caso_service = CasoService()
    caso = caso_service.find_by_id(id)
    if not caso:
        raise NotFoundException(resource="Caso", resource_id=id)

    return success_response(data=asdict(caso))


@caso_controller.route("/", methods=["POST"])
@authenticated
def create():
    current_user: UserInfo = RequestContext.get_current_user()
    caso_service = CasoService()

    json_data = cast(dict[str, Any], request.get_json(force=True))
    caso_input = CasoCreateInput(**json_data)
    caso = caso_service.create(caso_input, criado_por_id=current_user.id)

    return success_response(
        data=asdict(caso), message="Caso criado com sucesso", status_code=201
    )


@caso_controller.route("/<int:id>", methods=["PUT"])
@authenticated
def update(id: int):
    current_user: UserInfo = RequestContext.get_current_user()
    caso_service = CasoService()

    json_data = cast(dict[str, Any], request.get_json(force=True))
    caso_input = CasoUpdateInput(**json_data)
    caso = caso_service.update(id, caso_input, modificado_por_id=current_user.id)

    return success_response(data=asdict(caso), message="Caso atualizado com sucesso")


@caso_controller.route("/<int:id>", methods=["DELETE"])
@authorized("admin")
def delete(id: int):
    caso_service = CasoService()
    deleted = caso_service.soft_delete(id)
    if not deleted:
        raise NotFoundException(resource="Caso", resource_id=id)

    return success_response(message="Caso inativado com sucesso")


@caso_controller.route("/<int:id>/deferir", methods=["PATCH"])
@authenticated
def deferir(id: int):
    current_user: UserInfo = RequestContext.get_current_user()
    caso_service = CasoService()
    caso = caso_service.deferir(id, modificado_por_id=current_user.id)
    if not caso:
        raise NotFoundException(resource="Caso", resource_id=id)

    return success_response(data=asdict(caso), message="Caso deferido com sucesso")


@caso_controller.route("/<int:id>/indeferir", methods=["PATCH"])
@authenticated
def indeferir(id: int):
    current_user: UserInfo = RequestContext.get_current_user()
    caso_service = CasoService()

    json_data = cast(dict[str, Any], request.get_json(force=True))
    justificativa = json_data.get("justif_indeferimento", "")

    caso = caso_service.indeferir(
        id, justificativa=justificativa, modificado_por_id=current_user.id
    )
    if not caso:
        raise NotFoundException(resource="Caso", resource_id=id)

    return success_response(data=asdict(caso), message="Caso indeferido com sucesso")


@caso_controller.route("/<int:caso_id>/processos", methods=["GET"])
@authenticated
def get_processos_by_caso(caso_id: int):
    processo_service = ProcessoService()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )

    result = processo_service.search_by_caso(
        page_params=PageParams(page=page, per_page=per_page),
        caso_id=caso_id,
        search=search,
        show_inactive=show_inactive.value,
    )

    return success_response(data=result.to_dict())


@caso_controller.route("/<int:caso_id>/processos", methods=["POST"])
@authenticated
def create_processo(caso_id: int):
    current_user: UserInfo = RequestContext.get_current_user()
    processo_service = ProcessoService()

    json_data = cast(dict[str, Any], request.get_json(force=True))
    processo_input = ProcessoCreateInput(**json_data)
    processo = processo_service.create(
        caso_id=caso_id,
        processo_input=processo_input,
        criado_por_id=current_user.id,
    )

    return success_response(
        data=asdict(processo),
        message="Processo criado com sucesso",
        status_code=201,
    )


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["GET"])
@authenticated
def get_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    processo = processo_service.validate_processo_for_caso(processo_id, caso_id)
    if not processo:
        raise NotFoundException(resource="Processo", resource_id=processo_id)

    return success_response(data=asdict(processo))


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["PUT"])
@authenticated
def update_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    existing_processo = processo_service.validate_processo_for_caso(
        processo_id, caso_id
    )
    if not existing_processo:
        raise NotFoundException(resource="Processo", resource_id=processo_id)

    json_data = cast(dict[str, Any], request.get_json(force=True))
    processo_input = ProcessoUpdateInput(**json_data)
    processo = processo_service.update(processo_id, processo_input)
    if not processo:
        raise NotFoundException(resource="Processo", resource_id=processo_id)

    return success_response(
        data=asdict(processo), message="Processo atualizado com sucesso"
    )


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["DELETE"])
@authorized("admin")
def delete_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    existing_processo = processo_service.validate_processo_for_caso(
        processo_id, caso_id
    )
    if not existing_processo:
        raise NotFoundException(resource="Processo", resource_id=processo_id)

    result = processo_service.soft_delete(processo_id)

    if not result:
        raise NotFoundException(resource="Processo", resource_id=processo_id)

    return success_response(message="Processo inativado com sucesso")


@caso_controller.route("/<int:caso_id>/eventos", methods=["POST"])
@authenticated
def create_evento(caso_id: int):
    current_user: UserInfo = RequestContext.get_current_user()
    evento_service = EventoService()
    EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")

    form_data: dict[str, Any] = {
        "tipo": request.form.get("tipo"),
        "data_evento": request.form.get("data_evento"),
        "status": request.form.get("status", "true").lower() == "true",
        "descricao": request.form.get("descricao"),
    }

    id_usuario_responsavel = request.form.get("id_usuario_responsavel")
    form_data["id_usuario_responsavel"] = (
        int(id_usuario_responsavel) if id_usuario_responsavel else None
    )

    if "arquivo" in request.files:
        file = request.files["arquivo"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            os.makedirs(EVENTO_FILES_DIR, exist_ok=True)

            filepath = os.path.join(EVENTO_FILES_DIR, filename)
            file.save(filepath)

            form_data["arquivo"] = filepath

    evento_input = EventoCreateInput(**form_data)
    evento = evento_service.create(
        caso_id=caso_id,
        evento_input=evento_input,
        criado_por_id=current_user.id,
    )

    return success_response(
        data=asdict(evento), message="Evento criado com sucesso", status_code=201
    )


@caso_controller.route("/<int:caso_id>/eventos", methods=["GET"])
@authenticated
def get_eventos_by_caso(caso_id: int):
    evento_service = EventoService()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    result = evento_service.find_by_caso_id(
        caso_id=caso_id,
        page_params=PageParams(page=page, per_page=per_page),
    )

    return success_response(data=result.to_dict())


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["GET"])
@authenticated
def get_evento(caso_id: int, evento_id: int):
    evento_service = EventoService()

    evento = evento_service.validate_evento_for_caso(evento_id, caso_id)
    if not evento:
        raise NotFoundException(resource="Evento", resource_id=evento_id)

    return success_response(data=asdict(evento))


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["PUT"])
@authenticated
def update_evento(caso_id: int, evento_id: int):
    evento_service = EventoService()
    EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")

    existing_evento = evento_service.validate_evento_for_caso(evento_id, caso_id)
    if not existing_evento:
        raise NotFoundException(resource="Evento", resource_id=evento_id)

    form_data: dict[str, Any] = {}

    if request.form.get("tipo"):
        form_data["tipo"] = request.form.get("tipo")

    if request.form.get("data_evento"):
        form_data["data_evento"] = request.form.get("data_evento")

    if request.form.get("descricao"):
        form_data["descricao"] = request.form.get("descricao")

    if request.form.get("id_usuario_responsavel"):
        form_data["id_usuario_responsavel"] = int(
            request.form.get("id_usuario_responsavel")
        )

    if request.form.get("status"):
        form_data["status"] = request.form.get("status", "true").lower() == "true"

    if "arquivo" in request.files:
        file = request.files["arquivo"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            os.makedirs(EVENTO_FILES_DIR, exist_ok=True)

            filepath = os.path.join(EVENTO_FILES_DIR, filename)
            file.save(filepath)

            form_data["arquivo"] = filepath

    data_evento = form_data.get("data_evento")
    if data_evento:
        try:
            form_data["data_evento"] = parser.parse(data_evento).date()
        except (ValueError, TypeError) as exc:
            raise ValidationException(
                "Data de evento inválida", field="data_evento"
            ) from exc

    evento_input = EventoUpdateInput(**form_data)
    evento = evento_service.update(evento_id, evento_input)
    if not evento:
        raise NotFoundException(resource="Evento", resource_id=evento_id)

    return success_response(
        data=asdict(evento), message="Evento atualizado com sucesso"
    )


@caso_controller.route(
    "/<int:caso_id>/eventos/<int:evento_id>/download", methods=["GET"]
)
@authenticated
def download_evento_file(caso_id: int, evento_id: int):
    evento_service = EventoService()

    filepath, message = evento_service.get_evento_file_for_download(evento_id, caso_id)

    if not filepath:
        if message == "Evento não encontrado ou não pertence ao caso":
            raise NotFoundException(resource="Evento", resource_id=evento_id)
        raise FileOperationException(message, operation="download")

    return send_file(filepath, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos", methods=["GET"])
@authenticated
def get_arquivos_by_caso(caso_id: int):
    caso_service = CasoService()
    arquivos = caso_service.find_arquivos_by_caso_id(caso_id)

    return success_response(
        data={"arquivos": [asdict(arquivo) for arquivo in arquivos]}
    )


@caso_controller.route("/<int:caso_id>/arquivos", methods=["POST"])
@authenticated
def upload_arquivo_caso(caso_id: int):
    caso_service = CasoService()

    if "arquivo" not in request.files:
        raise ValidationException("Nenhum arquivo enviado", field="arquivo")

    file = request.files["arquivo"]
    arquivo = caso_service.upload_arquivo(caso_id, file)

    return success_response(
        data=asdict(arquivo),
        message="Arquivo carregado com sucesso",
        status_code=201,
    )


@caso_controller.route(
    "/<int:caso_id>/arquivos/<int:arquivo_id>/download", methods=["GET"]
)
@authenticated
def download_arquivo_caso(caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    filepath = caso_service.get_arquivo_for_download(arquivo_id, caso_id)

    return send_file(filepath, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos/<int:arquivo_id>", methods=["DELETE"])
@authenticated
def delete_arquivo_caso(caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    caso_service.delete_arquivo(arquivo_id, caso_id)

    return success_response(message="Arquivo removido com sucesso")
