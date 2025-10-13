import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, cast
from flask import send_file

from flask import Blueprint, make_response, request
from werkzeug.utils import secure_filename

from gestaolegal.common import PageParams
from gestaolegal.config import Config
from gestaolegal.models.evento_input import EventoUpdateInput
from gestaolegal.models.caso_input import CasoCreateInput, CasoUpdateInput
from gestaolegal.models.evento_input import EventoCreateInput
from gestaolegal.models.processo_input import ProcessoCreateInput, ProcessoUpdateInput
from gestaolegal.models.user import User
from gestaolegal.services.caso_service import CasoService
from gestaolegal.services.evento_service import EventoService
from gestaolegal.services.processo_service import ProcessoService
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

EVENTO_FILES_DIR = os.path.join(Config.STATIC_ROOT_DIR, "eventos")

caso_controller = Blueprint("caso_api", __name__)


@caso_controller.route("/", methods=["GET"])
@api_auth_required
def get(current_user: User):
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
def find_by_id(current_user: User, id: int):
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
def delete(current_user: User, id: int):
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
@caso_controller.route("/<int:caso_id>/processo", methods=["GET"])
@api_auth_required
def get_processos_by_caso(current_user: User, caso_id: int):
    processo_service = ProcessoService()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    show_inactive = (
        request.args.get("show_inactive", default="false", type=str).lower() == "true"
    )

    return processo_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive,
        caso_id=caso_id,
    ).to_dict()


@caso_controller.route("/<int:caso_id>/processos", methods=["POST"])
@caso_controller.route("/<int:caso_id>/processo", methods=["POST"])
@api_auth_required
def create_processo(current_user: User, caso_id: int):
    processo_service = ProcessoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        json_data["id_caso"] = caso_id
        processo_input = ProcessoCreateInput(**json_data)
        processo_input.id_caso = caso_id
        processo = processo_service.create(
            processo_input, criado_por_id=current_user.id
        )
    except Exception as e:
        logger.error(f"Error creating processo: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(processo)


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["GET"])
@api_auth_required
def get_processo(current_user: User, caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    processo = processo_service.find_by_id(processo_id)
    if not processo:
        return make_response("Processo não encontrado", 404)

    if processo.id_caso != caso_id:
        return make_response("Processo não pertence ao caso", 400)

    return asdict(processo)


@caso_controller.route("/<int:caso_id>/processos/<int:processo_id>", methods=["PUT"])
@api_auth_required
def update_processo(current_user: User, caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        processo_input = ProcessoUpdateInput(**json_data)

        existing_processo = processo_service.find_by_id(processo_id)
        if not existing_processo:
            return make_response("Processo não encontrado", 404)

        if existing_processo.id_caso != caso_id:
            return make_response("Processo não pertence ao caso", 400)

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
def delete_processo(current_user: User, caso_id: int, processo_id: int):
    processo_service = ProcessoService()

    existing_processo = processo_service.find_by_id(processo_id)
    if not existing_processo:
        return make_response("Processo não encontrado", 404)

    if existing_processo.id_caso != caso_id:
        return make_response("Processo não pertence ao caso", 400)

    result = processo_service.soft_delete(processo_id)

    if not result:
        return make_response("Processo não encontrado", 404)

    return make_response("Processo inativado com sucesso", 200)


@caso_controller.route("/<int:caso_id>/eventos", methods=["POST"])
@caso_controller.route("/<int:caso_id>/evento", methods=["POST"])
@api_auth_required
def create_evento(current_user: User, caso_id: int):
    evento_service = EventoService()

    try:
        if request.is_json:
            json_data = cast(dict[str, Any], request.get_json(force=True))
            form_data: dict[str, Any] = {
                "id_caso": caso_id,
                "tipo": json_data.get("tipo_evento") or json_data.get("tipo"),
                "data_evento": json_data.get("data_evento"),
                "status": json_data.get("status", True),
            }

            if json_data.get("num_evento"):
                form_data["num_evento"] = json_data.get("num_evento")

            if json_data.get("descricao"):
                form_data["descricao"] = json_data.get("descricao")

            if json_data.get("id_usuario_responsavel"):
                form_data["id_usuario_responsavel"] = json_data.get(
                    "id_usuario_responsavel"
                )
        else:
            form_data = {
                "id_caso": caso_id,
                "tipo": request.form.get("tipo"),
                "data_evento": request.form.get("data_evento"),
                "status": request.form.get("status", "true").lower() == "true",
            }

            if request.form.get("num_evento"):
                form_data["num_evento"] = int(request.form.get("num_evento"))

            if request.form.get("descricao"):
                form_data["descricao"] = request.form.get("descricao")

            if request.form.get("id_usuario_responsavel"):
                form_data["id_usuario_responsavel"] = int(
                    request.form.get("id_usuario_responsavel")
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
        evento = evento_service.create(evento_input, criado_por_id=current_user.id)
    except Exception as e:
        logger.error(f"Error creating evento: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(evento)


@caso_controller.route("/<int:caso_id>/eventos", methods=["GET"])
@caso_controller.route("/<int:caso_id>/evento", methods=["GET"])
@api_auth_required
def get_eventos_by_caso(caso_id: int):
    evento_service = EventoService()
    return evento_service.find_by_caso_id(caso_id).to_dict()


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["GET"])
@api_auth_required
def get_evento(caso_id: int, evento_id: int):
    evento_service = EventoService()

    evento = evento_service.find_by_id(evento_id)
    if not evento:
        return make_response("Evento não encontrado", 404)

    if evento.id_caso != caso_id:
        return make_response("Evento não pertence ao caso", 400)

    return asdict(evento)


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>", methods=["PUT"])
@api_auth_required
def update_evento(current_user: User, caso_id: int, evento_id: int):

    evento_service = EventoService()

    try:
        existing_evento = evento_service.find_by_id(evento_id)
        if not existing_evento:
            return make_response("Evento não encontrado", 404)

        if existing_evento.id_caso != caso_id:
            return make_response("Evento não pertence ao caso", 400)

        if request.is_json:
            json_data = cast(dict[str, Any], request.get_json(force=True))
            evento_input = EventoUpdateInput(**json_data)
        else:
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

            evento_input = EventoUpdateInput(**form_data)

        evento = evento_service.update(evento_id, evento_input)
    except ValueError as e:
        return make_response(str(e), 404)
    except Exception as e:
        logger.error(f"Error updating evento {evento_id}: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    if not evento:
        return make_response("Erro ao atualizar evento", 404)

    return asdict(evento)


@caso_controller.route("/<int:caso_id>/eventos/<int:evento_id>/download", methods=["GET"])
@api_auth_required
def download_evento_file(current_user: User, caso_id: int, evento_id: int):
    evento_service = EventoService()

    evento = evento_service.find_by_id(evento_id)
    if not evento:
        return make_response("Evento não encontrado", 404)

    if evento.id_caso != caso_id:
        return make_response("Evento não pertence ao caso", 400)

    if not evento.arquivo:
        return make_response("Evento não possui arquivo", 404)

    if not os.path.exists(evento.arquivo):
        return make_response("Arquivo não encontrado no servidor", 404)

    return send_file(evento.arquivo, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos", methods=["GET"])
@api_auth_required
def get_arquivos_by_caso(current_user: User, caso_id: int):
    caso_service = CasoService()
    arquivos = caso_service.find_arquivos_by_caso_id(caso_id)

    return {"arquivos": [asdict(arquivo) for arquivo in arquivos]}


@caso_controller.route("/<int:caso_id>/arquivos", methods=["POST"])
@api_auth_required
def upload_arquivo_caso(current_user: User, caso_id: int):
    caso_service = CasoService()

    if "arquivo" not in request.files:
        return make_response("Nenhum arquivo enviado", 400)

    file = request.files["arquivo"]
    arquivo, message = caso_service.upload_arquivo(caso_id, file)

    if not arquivo:
        return make_response(message, 404 if "não encontrado" in message else 400)

    return asdict(arquivo)


@caso_controller.route("/<int:caso_id>/arquivos/<int:arquivo_id>/download", methods=["GET"])
@api_auth_required
def download_arquivo_caso(current_user: User, caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    filepath, message = caso_service.get_arquivo_for_download(arquivo_id, caso_id)

    if not filepath:
        return make_response(message, 404)

    return send_file(filepath, as_attachment=True)


@caso_controller.route("/<int:caso_id>/arquivos/<int:arquivo_id>", methods=["DELETE"])
@api_auth_required
def delete_arquivo_caso(current_user: User, caso_id: int, arquivo_id: int):
    caso_service = CasoService()
    success, message = caso_service.delete_arquivo(arquivo_id, caso_id)

    if not success:
        return make_response(message, 404)

    return make_response(message, 200)
