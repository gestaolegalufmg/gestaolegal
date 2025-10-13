import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, cast

from dateutil import parser
from flask import Blueprint, make_response, request, send_file
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams
from gestaolegal.config import Config
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.evento_input import EventoCreateInput, EventoUpdateInput
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.models.user import User
from gestaolegal.services.caso_service import CasoService
from gestaolegal.services.evento_service import EventoService
from gestaolegal.services.processo_service import ProcessoService
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

caso_controller = Blueprint("caso_api", __name__)


@caso_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )
    situacao_deferimento = request.args.get(
        "situacao_deferimento", default=None, type=str
    )

    caso_service = CasoService()

    return caso_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive,
        situacao_deferimento=situacao_deferimento,
    ).to_dict()


@caso_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    caso_service = CasoService()

    caso = caso_service.find_by_id(id)
    if not caso:
        return make_response("Caso não encontrado", 404)

    return asdict(caso)


@caso_controller.route("/", methods=["POST"])
@api_auth_required
def create(current_user: User):
    caso_service = CasoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        caso_input = CasoCreateInput(**json_data)
        caso = caso_service.create(caso_input, criado_por_id=current_user.id)
    except Exception as e:
        logger.error(f"Error creating caso: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(caso)


@caso_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(current_user: User, id: int):
    caso_service = CasoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        caso_input = CasoUpdateInput(**json_data)
        caso = caso_service.update(id, caso_input, modificado_por_id=current_user.id)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating caso {id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not caso:
        return make_response("Erro ao atualizar caso", 404)

    return asdict(caso)


@caso_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    caso_service = CasoService()
    result = caso_service.soft_delete(id)

    if not result:
        return make_response("Caso não encontrado", 404)

    return make_response("Caso inativado com sucesso", 200)


@caso_controller.route("/<int:id>/deferir", methods=["PATCH"])
@api_auth_required
def deferir(current_user: User, id: int):
    caso_service = CasoService()

    try:
        caso = caso_service.deferir(id, modificado_por_id=current_user.id)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error deferring caso {id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not caso:
        return make_response("Erro ao deferir caso", 404)

    return asdict(caso)


@caso_controller.route("/<int:id>/indeferir", methods=["PATCH"])
@api_auth_required
def indeferir(current_user: User, id: int):
    caso_service = CasoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        justificativa = json_data.get("justif_indeferimento", "")

        caso = caso_service.indeferir(
            id, justificativa=justificativa, modificado_por_id=current_user.id
        )
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error indeferring caso {id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not caso:
        return make_response("Erro ao indeferir caso", 404)

    return asdict(caso)


@caso_controller.route("/<int:caso_id>/processos", methods=["GET"])
@api_auth_required
def get_processos_by_caso(caso_id: int):
    processo_service = ProcessoService()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )

    return processo_service.search_by_caso(
        page_params=PageParams(page=page, per_page=per_page),
        caso_id=caso_id,
        search=search,
        show_inactive=show_inactive,
    ).to_dict()


@caso_controller.route("/<int:caso_id>/processos", methods=["POST"])
@api_auth_required
def create_processo(current_user: User, caso_id: int):
    processo_service = ProcessoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        processo_input = ProcessoCreateInput(**json_data)
        processo = processo_service.create(
            caso_id=caso_id,
            processo_input=processo_input,
            criado_por_id=current_user.id,
        )
    except Exception as e:
        logger.error(f"Error creating processo: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(processo)


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["GET"])
@api_auth_required
def get_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    processo = processo_service.validate_processo_for_caso(processo_id, caso_id)
    if not processo:
        return make_response("Processo não encontrado ou não pertence ao caso", 404)

    return asdict(processo)


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["PUT"])
@api_auth_required
def update_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        processo_input = ProcessoUpdateInput(**json_data)

        existing_processo = processo_service.validate_processo_for_caso(
            processo_id, caso_id
        )
        if not existing_processo:
            return make_response("Processo não encontrado ou não pertence ao caso", 404)

        processo = processo_service.update(processo_id, processo_input)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating processo {processo_id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not processo:
        return make_response("Erro ao atualizar processo", 404)

    return asdict(processo)


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["DELETE"])
@api_auth_required
def delete_processo(caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    existing_processo = processo_service.validate_processo_for_caso(
        processo_id, caso_id
    )
    if not existing_processo:
        return make_response("Processo não encontrado ou não pertence ao caso", 404)

    result = processo_service.soft_delete(processo_id)

    if not result:
        return make_response("Processo não encontrado", 404)

    return make_response("Processo inativado com sucesso", 200)


@caso_controller.route("/<int:caso_id>/eventos", methods=["POST"])
@api_auth_required
def create_evento(current_user: User, caso_id: int):
    evento_service = EventoService()
    EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")

    try:
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
    except Exception as e:
        logger.error(f"Error creating evento: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(evento)


@caso_controller.route("/<int:caso_id>/eventos", methods=["GET"])
@api_auth_required
def get_eventos_by_caso(caso_id: int):
    evento_service = EventoService()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    return evento_service.find_by_caso_id(
        caso_id=caso_id,
        page_params=PageParams(page=page, per_page=per_page),
    ).to_dict()


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["GET"])
@api_auth_required
def get_evento(caso_id: int, evento_id: int):
    evento_service = EventoService()

    evento = evento_service.validate_evento_for_caso(evento_id, caso_id)
    if not evento:
        return make_response("Evento não encontrado ou não pertence ao caso", 404)

    return asdict(evento)


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["PUT"])
@api_auth_required
def update_evento(caso_id: int, evento_id: int):
    evento_service = EventoService()
    EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")

    try:
        existing_evento = evento_service.validate_evento_for_caso(evento_id, caso_id)
        if not existing_evento:
            logger.error(f"Evento not found with id: {evento_id}")
            return make_response("Evento não encontrado ou não pertence ao caso", 404)

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
            form_data["data_evento"] = parser.parse(data_evento)

        evento_input = EventoUpdateInput(**form_data)
        evento = evento_service.update(evento_id, evento_input)
    except ValueError as e:
        logger.error(f"Error updating evento {evento_id}: {str(e)}", exc_info=True)
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating evento {evento_id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not evento:
        return make_response("Erro ao atualizar evento", 404)

    return asdict(evento)


@caso_controller.route(
    "/<int:caso_id>/eventos/<int:evento_id>/download", methods=["GET"]
)
@api_auth_required
def download_evento_file(caso_id: int, evento_id: int):
    evento_service = EventoService()

    filepath, message = evento_service.get_evento_file_for_download(evento_id, caso_id)

    if not filepath:
        return make_response(message, 404)

    return send_file(filepath, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos", methods=["GET"])
@api_auth_required
def get_arquivos_by_caso(caso_id: int):
    caso_service = CasoService()
    arquivos = caso_service.find_arquivos_by_caso_id(caso_id)

    return {"arquivos": [asdict(arquivo) for arquivo in arquivos]}


@caso_controller.route("/<int:caso_id>/arquivos", methods=["POST"])
@api_auth_required
def upload_arquivo_caso(caso_id: int):
    caso_service = CasoService()

    if "arquivo" not in request.files:
        return make_response("Nenhum arquivo enviado", 400)

    file = request.files["arquivo"]
    arquivo, message = caso_service.upload_arquivo(caso_id, file)

    if not arquivo:
        return make_response(message, 404 if "não encontrado" in message else 400)

    return asdict(arquivo)


@caso_controller.route(
    "/<int:caso_id>/arquivos/<int:arquivo_id>/download", methods=["GET"]
)
@api_auth_required
def download_arquivo_caso(caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    filepath, message = caso_service.get_arquivo_for_download(arquivo_id, caso_id)

    if not filepath:
        return make_response(message, 404)

    return send_file(filepath, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos/<int:arquivo_id>", methods=["DELETE"])
@api_auth_required
def delete_arquivo_caso(caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    success, message = caso_service.delete_arquivo(arquivo_id, caso_id)

    if not success:
        return make_response(message, 404)

    return make_response(message, 200)
