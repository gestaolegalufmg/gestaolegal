from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, request

from gestaolegal.models.roteiro_input import RoteiroUpsertInput
from gestaolegal.services.roteiro_service import RoteiroService
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.api_response import success_response

roteiro_controller = Blueprint("roteiro_api", __name__)


@roteiro_controller.route("", methods=["GET"])
@authenticated
def get_all():
    service = RoteiroService()
    roteiros = service.get_all()
    return success_response(data=[asdict(r) for r in roteiros])


@roteiro_controller.route("/", methods=["PUT"])
@authorized("admin", "orient", "colab_ext")
def upsert():
    service = RoteiroService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    roteiro_input = RoteiroUpsertInput(**json_data)
    roteiro = service.upsert(roteiro_input.area_direito, roteiro_input.link)
    return success_response(
        data=asdict(roteiro), message="Roteiro atualizado com sucesso"
    )
