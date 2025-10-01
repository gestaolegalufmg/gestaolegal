import logging

from flask import Blueprint, make_response, request

from gestaolegal.common import PageParams
from gestaolegal.common.constants.atendido import TipoBusca
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.utils import StringBool
from gestaolegal.utils.api_responses import api_error, api_success
from gestaolegal.utils.api_decorators import api_auth_required

logger = logging.getLogger(__name__)

atendido_controller = Blueprint("atendido_api", __name__)


@atendido_controller.route("/", methods=["GET"])
@api_auth_required
def get():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    search = request.args.get("search", default="", type=str)
    tipo_busca = request.args.get("tipo_busca", default=TipoBusca.TODOS, type=TipoBusca)
    show_inactive = request.args.get("show_inactive", default=StringBool("false"), type=StringBool)


    atendido_service = AtendidoService()
    logger.info(f"Searching for atendidos with search: {search}, page: {page}, per_page: {per_page}")
    atendido = atendido_service.get(page_params=PageParams(page=page, per_page=per_page), valor_busca=search, tipo_busca=tipo_busca, show_inactive=show_inactive.value)

    logger.info(f"Returning {len(atendido.items)} atendidos")
    return atendido.to_dict()

@atendido_controller.route("/<int:id>", methods=["GET"])
@api_auth_required
def find_by_id(id: int):
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        atendido = atendido_service.find_by_id(id)
        
        if not atendido:
            return make_response(api_error("Atendido not found"), 404)
        
        logger.info(f"Returning atendido: {id}")
        return atendido.to_dict()
        
    except Exception as e:
        logger.error(f"Error in find_by_id: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)

@atendido_controller.route("/", methods=["POST"])
@api_auth_required
def create():
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        data = request.get_json()
        
        if not data:
            return make_response(api_error("No data provided"), 400)
        
        logger.info(f"Creating atendido with data keys: {list(data.keys())}")
        
        # Use the service method that handles JSON data properly
        result = atendido_service.create_atendido_from_json(data)
        
        if result.get("message") == "success":
            logger.info(f"Atendido created successfully with ID: {result.get('id')}")
            return api_success(result)
        else:
            logger.error(f"Failed to create atendido: {result.get('message')}")
            return make_response(api_error(result.get("message", "Unknown error")), 400)
            
    except ValueError as e:
        logger.warning(f"Validation error in create: {str(e)}")
        return make_response(api_error(str(e)), 400)
    except Exception as e:
        logger.error(f"Error in create: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)

@atendido_controller.route("/<int:id>", methods=["PUT"])
@api_auth_required
def update(id: int):
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        data = request.get_json()
        
        if not data:
            return make_response(api_error("No data provided"), 400)
        
        logger.info(f"Updating atendido {id} with data keys: {list(data.keys())}")
        
        # Check if atendido exists
        existing_atendido = atendido_service.find_by_id(id)
        if not existing_atendido:
            return make_response(api_error("Atendido not found"), 404)
        
        # Update the atendido
        updated_atendido = atendido_service.update(id, data)
        
        logger.info(f"Atendido {id} updated successfully")
        return updated_atendido.to_dict()
        
    except ValueError as e:
        logger.warning(f"Validation error in update: {str(e)}")
        return make_response(api_error(str(e)), 400)
    except Exception as e:
        logger.error(f"Error in update: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)

@atendido_controller.route("/<int:id>", methods=["DELETE"])
@api_auth_required
def delete(id: int):
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        
        # Check if atendido exists
        existing_atendido = atendido_service.find_by_id(id)
        if not existing_atendido:
            return make_response(api_error("Atendido not found"), 404)
        
        logger.info(f"Soft deleting atendido {id}")
        
        # Perform soft delete
        success = atendido_service.soft_delete(id)
        
        if success:
            logger.info(f"Atendido {id} soft deleted successfully")
            return api_success({"message": "Atendido deleted successfully"})
        else:
            logger.error(f"Failed to soft delete atendido {id}")
            return make_response(api_error("Failed to delete atendido"), 500)
        
    except Exception as e:
        logger.error(f"Error in delete: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)

@atendido_controller.route("/<int:id>/tornar-assistido", methods=["POST"])
@api_auth_required
def tornar_assistido(id: int):
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        data = request.get_json()
        
        if not data:
            return make_response(api_error("No data provided"), 400)
        
        logger.info(f"Converting atendido {id} to assistido with data keys: {list(data.keys())}")
        
        # Check if atendido exists
        existing_atendido = atendido_service.find_by_id(id)
        if not existing_atendido:
            return make_response(api_error("Atendido not found"), 404)
        
        # Create assistido from the atendido
        assistido = atendido_service.create_assistido(id, data)
        
        logger.info(f"Assistido created successfully for atendido {id}")
        return assistido.to_dict()
        
    except ValueError as e:
        logger.warning(f"Validation error in tornar_assistido: {str(e)}")
        return make_response(api_error(str(e)), 400)
    except Exception as e:
        logger.error(f"Error in tornar_assistido: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)

@atendido_controller.route("/<int:id>/assistido", methods=["PUT"])
@api_auth_required
def update_assistido(id: int):
    # TODO: Check route logic
    try:
        atendido_service = AtendidoService()
        data = request.get_json()
        
        if not data:
            return make_response(api_error("No data provided"), 400)
        
        logger.info(f"Updating assistido for atendido {id} with data keys: {list(data.keys())}")
        
        # Check if atendido exists
        existing_atendido = atendido_service.find_by_id(id)
        if not existing_atendido:
            return make_response(api_error("Atendido not found"), 404)
        
        # The service expects both atendido_data and assistido_data
        # We need to separate them from the request data
        # TODO: Need to clarify how the frontend will send this data structure
        # For now, assuming the data contains both atendido and assistido fields
        atendido_data = {}
        assistido_data = {}
        
        # Separate fields based on common patterns
        # TODO: This separation logic may need refinement based on actual frontend data structure
        assistido_fields = [
            'sexo', 'profissao', 'raca', 'rg', 'grau_instrucao', 'salario', 
            'beneficio', 'qual_beneficio', 'contribui_inss', 'qtd_pessoas_moradia',
            'renda_familiar', 'participacao_renda', 'tipo_moradia', 'possui_outros_imoveis',
            'quantos_imoveis', 'possui_veiculos', 'possui_veiculos_obs', 'quantos_veiculos',
            'ano_veiculo', 'doenca_grave_familia', 'pessoa_doente', 'pessoa_doente_obs',
            'gastos_medicacao', 'obs'
        ]
        
        for key, value in data.items():
            if key in assistido_fields:
                assistido_data[key] = value
            else:
                atendido_data[key] = value
        
        # Update both atendido and assistido
        updated_assistido = atendido_service.update_assistido(id, atendido_data, assistido_data)
        
        logger.info(f"Assistido updated successfully for atendido {id}")
        return updated_assistido.to_dict()
        
    except ValueError as e:
        logger.warning(f"Validation error in update_assistido: {str(e)}")
        return make_response(api_error(str(e)), 400)
    except Exception as e:
        logger.error(f"Error in update_assistido: {str(e)}", exc_info=True)
        return make_response(api_error(f"Internal server error: {str(e)}"), 500)
