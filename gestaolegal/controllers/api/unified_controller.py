import logging

from flask import Blueprint, request

from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

unified_controller = Blueprint("unified_api", __name__)


@unified_controller.route("/", methods=["GET"])
@api_auth_required
def search():
    search_string = request.args.get("search", default="", type=str)
    return {"message": "Not implemented"}
