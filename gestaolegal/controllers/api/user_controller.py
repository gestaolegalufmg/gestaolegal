import logging
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.user import User
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils import StringBool
from gestaolegal.utils.api_decorators import api_auth_required


logger = logging.getLogger(__name__)

user_controller = Blueprint("user", __name__)

@user_controller.route("/me", methods=["GET"])
@api_auth_required
def get_me(current_user: User):
    return current_user.to_dict()

@user_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    funcao = request.args.get("funcao", default="all", type=str)
    show_inactive = request.args.get("show_inactive", default=StringBool("false"), type=StringBool)

    user_service = UsuarioService()
    logger.info(f"Getting users with search: {search}, funcao: {funcao}, show_inactive: {show_inactive.value}")
    return user_service.search(page_params=PageParams(page=page, per_page=per_page), search=search, show_inactive=show_inactive.value, role=funcao).to_dict()

@user_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    user_service = UsuarioService()
    logger.info(f"Getting user by id: {id}")
    user = user_service.find_by_id(id)
    if not user:
        return make_response("User not found", 404)

    logger.info(f"User found: {user}")
    return user.to_dict()

@user_controller.route("/", methods=["POST"])
@api_auth_required
def create(current_user: User):
    logger.info(f"Creating user")
    user_service = UsuarioService()

    try:
        user_data = cast(dict[str, Any], request.get_json(force=True))
        user = user_service.create(user_data, criado_por=cast(int, current_user.id))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    logger.info(f"User created: {user}")

    return user.to_dict()

@user_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int, current_user: User):
    logger.info(f"Updating user: {id}")
    user_service = UsuarioService()
    user_data: Any = request.get_json(force=True)

    user = user_service.update(id, user_data, current_user.id)
    if not user:
        logger.error(f"User not found: {id}")
        return make_response("User not found", 404)

    logger.info(f"User updated: {user}")
    return user.to_dict()

@user_controller.route("/me", methods=["PUT"])
@api_auth_required
def update_me(current_user: User):
    logger.info(f"Updating user: {current_user.id}")
    user_service = UsuarioService()
    user_data: Any = request.get_json(force=True)

    user = user_service.update(
        cast(int, current_user.id), # id cant be none here
        user_data,
        current_user.id
    )

    if not user:
        logger.error(f"Error wh updating user: {current_user.id}")
        return make_response("Error wh updating user", 404)

    logger.info(f"User updated: {user}")
    return user.to_dict()

@user_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    logger.info(f"Deactivating user: {id}")

    user_service = UsuarioService()
    user = user_service.soft_delete(id)

    logger.info(f"User deactivated: {user}")

    return make_response("User deactivated", 200)
