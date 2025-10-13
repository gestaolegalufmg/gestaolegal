import logging
from dataclasses import asdict
from typing import Any, cast

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.models.user_input import UserCreateInput, UserUpdateInput
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils import StringBool
from gestaolegal.utils.api_decorators import authenticated, authorized
from gestaolegal.utils.request_context import RequestContext

logger = logging.getLogger(__name__)

user_controller = Blueprint("user", __name__)


@user_controller.route("/me", methods=["GET"])
@authenticated
def get_me():
    current_user = RequestContext.get_current_user()
    return asdict(current_user)


@user_controller.route("/", methods=["GET"])
@authorized("admin")
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    funcao = request.args.get("funcao", default="all", type=str)
    show_inactive = request.args.get(
        "show_inactive", default=StringBool("false"), type=StringBool
    )

    user_service = UsuarioService()

    return user_service.search(
        page_params=PageParams(page=page, per_page=per_page),
        search=search,
        show_inactive=show_inactive.value,
        role=funcao,
    ).to_dict()


@user_controller.route("/<int:id>", methods=["GET"])
@authorized("admin")
def find_by_id(id: int):
    user_service = UsuarioService()
    user = user_service.find_by_id(id)
    if not user:
        return make_response("User not found", 404)

    return asdict(user)


@user_controller.route("/", methods=["POST"])
@authorized("admin")
def create():
    current_user = RequestContext.get_current_user()
    user_service = UsuarioService()

    try:
        json_data = cast(dict[str, Any], request.get_json(force=True))
        user_input = UserCreateInput.model_validate(json_data)
        user = user_service.create(user_input, criado_por=cast(int, current_user.id))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        return make_response(str(e), 500)

    return asdict(user)


@user_controller.route("/<int:id>", methods=["PUT"])
@authorized("admin")
def update(id: int):
    current_user = RequestContext.get_current_user()
    user_service = UsuarioService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    user_input = UserUpdateInput.model_validate(json_data)

    user = user_service.update(id, user_input, current_user.id)
    if not user:
        return make_response("User not found", 404)

    return asdict(user)


@user_controller.route("/me", methods=["PUT"])
@authenticated
def update_me():
    current_user = RequestContext.get_current_user()
    user_service = UsuarioService()
    json_data = cast(dict[str, Any], request.get_json(force=True))
    user_input = UserUpdateInput.model_validate(json_data)

    user = user_service.update(
        cast(int, current_user.id),
        user_input,
        current_user.id,
    )

    if not user:
        return make_response("Error wh updating user", 404)

    return asdict(user)


@user_controller.route("/<int:id>", methods=["DELETE"])
@authorized("admin")
def delete(id: int):
    user_service = UsuarioService()
    user_service.soft_delete(id)

    return make_response("User deactivated", 200)


@user_controller.route("/<int:id>/password", methods=["PUT"])
@authenticated
def change_password(id: int):
    current_user = RequestContext.get_current_user()
    try:
        data = cast(dict[str, Any], request.get_json(force=True))
        current_password = data.get("currentPassword")
        new_password = data.get("newPassword")
        from_admin = data.get("fromAdmin", False)

        if not new_password:
            return make_response("New password is required", 400)

        is_admin = current_user.urole == "admin"
        is_own_profile = current_user.id == id

        if not is_admin and not is_own_profile:
            return make_response("Unauthorized to change this password", 403)

        if not from_admin and not current_password:
            return make_response("Current password is required", 400)

        user_service = UsuarioService()
        user = user_service.change_password(
            user_id=id,
            current_password=current_password,
            new_password=new_password,
            is_admin_change=from_admin and is_admin,
        )

        if not user:
            return make_response("Failed to change password", 500)

        return make_response("Password changed successfully", 200)

    except ValueError as e:
        return make_response({"message": str(e)}, 400)
    except Exception as e:
        logger.error(f"Unexpected error changing password: {str(e)}", exc_info=True)
        return make_response({"message": "Internal server error"}, 500)
