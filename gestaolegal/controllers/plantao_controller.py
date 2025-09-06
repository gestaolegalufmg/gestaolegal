import logging
from dataclasses import dataclass
from datetime import date, datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.plantao import (
    AbrirPlantaoForm,
    FecharPlantaoForm,
    SelecionarDuracaoPlantaoForm,
)
from gestaolegal.services.atendido_service import AtendidoService
from gestaolegal.services.plantao_service import PlantaoService
from gestaolegal.utils.decorators import login_required
from gestaolegal.utils.plantao_utils import numero_plantao_a_marcar

logger = logging.getLogger(__name__)


@dataclass
class CardInfo:
    title: str
    body: dict[str, str | None] | str


plantao_controller = Blueprint(
    "plantao", __name__, template_folder="../static/templates"
)

data_atual = datetime.now().date()


@plantao_controller.route("/pagina_plantao", methods=["POST", "GET"])
@login_required()
def pg_plantao():
    logger.info("Entering pg_plantao route")
    plantao_service = PlantaoService()

    dias_usuario_marcado = plantao_service.get_dias_usuario_marcado(current_user.id)
    plantao = plantao_service.get_plantao_ativo()

    plantao_service.apaga_dias_marcados(plantao, dias_usuario_marcado)
    try:
        if (
            current_user.urole
            not in [
                UserRole.ADMINISTRADOR,
                UserRole.COLAB_PROJETO,
            ]
        ) and (plantao and plantao.data_abertura is None):
            flash("O plantão não está aberto!")
            return redirect(url_for("principal.index"))

        dias_usuario_atual = plantao_service.get_dias_usuario_marcado(current_user.id)

        return render_template(
            "plantao/pagina_plantao.html",
            datas_plantao=dias_usuario_atual,
            numero_plantao=numero_plantao_a_marcar(current_user.id),
            data_atual=data_atual,
        )
    except AttributeError:
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))


@plantao_controller.route("/ajax_obter_escala_plantao", methods=["GET"])
@login_required()
def ajax_obter_escala_plantao():
    plantao_service = PlantaoService()
    escala = plantao_service.get_escala_plantao()

    return current_app.response_class(
        response=json.dumps(escala), status=200, mimetype="application/json"
    )


@plantao_controller.route("/ajax_obter_duracao_plantao", methods=["GET", "POST"])
@login_required()
def ajax_obter_duracao_plantao():
    plantao_service = PlantaoService()
    dias_duracao = plantao_service.get_duracao_plantao()

    return current_app.response_class(
        response=json.dumps(dias_duracao), status=200, mimetype="application/json"
    )


@plantao_controller.route("/ajax_confirma_data_plantao", methods=["POST", "GET"])
@login_required()
def ajax_confirma_data_plantao():
    def cria_json(lista_datas, mensagem, tipo_mensagem: str):
        return {
            "lista_datas": lista_datas,
            "mensagem": mensagem,
            "tipo_mensagem": tipo_mensagem,
            "numero_plantao": numero_plantao_a_marcar(current_user.id),
        }

    plantao_service = PlantaoService()

    plantao = plantao_service.get_plantao_ativo()
    plantao_service.valida_fim_plantao(plantao)
    if (
        current_user.urole
        not in [
            UserRole.ADMINISTRADOR,
            UserRole.COLAB_PROJETO,
        ]
    ) and (plantao and plantao.data_abertura is None):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")
    data_marcada = date(int(ano), int(mes), int(dia))

    dias_usuario_marcado = plantao_service.get_dias_usuario_marcado(current_user.id)

    disponibilidade = plantao_service.verificar_disponibilidade_data(
        data_marcada, current_user.id, current_user.urole
    )

    if not disponibilidade["disponivel"]:
        resultado_json = cria_json(
            render_template(
                "plantao/componentes/lista_datas_plantao.html",
                data_atual=data_atual,
                datas_plantao=dias_usuario_marcado,
            ),
            disponibilidade["mensagem"],
            disponibilidade["tipo_mensagem"],
        )
        return current_app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if len(dias_usuario_marcado) >= 2 or (
        len(dias_usuario_marcado) >= 1 and current_user.urole == UserRole.ORIENTADOR
    ):
        resultado_json = cria_json(
            render_template(
                "plantao/componentes/lista_datas_plantao.html",
                datas_plantao=dias_usuario_marcado,
                data_atual=data_atual,
            ),
            "Você atingiu o limite de plantões cadastrados.",
            "warning",
        )
        return current_app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if plantao_service.marcar_data_plantao(data_marcada, current_user.id):
        mensagem = "Data de plantão cadastrada!"
        tipo_mensagem = "success"
    else:
        mensagem = "Erro ao cadastrar data de plantão."
        tipo_mensagem = "error"

    dias_usuario_atual = plantao_service.get_dias_usuario_marcado(current_user.id)
    resultado_json = cria_json(
        render_template(
            "plantao/componentes/lista_datas_plantao.html",
            datas_plantao=dias_usuario_atual,
            data_atual=data_atual,
        ),
        mensagem,
        tipo_mensagem,
    )
    return current_app.response_class(
        response=json.dumps(resultado_json), status=200, mimetype="application/json"
    )


@plantao_controller.route("/editar_plantao", methods=["GET"])
@login_required()
def editar_plantao():
    plantao_service = PlantaoService()

    if plantao_service.apagar_dias_marcados_usuario(current_user.id):
        flash(
            "Registro apagado. Por favor, selecione novamente os dias para o seu plantão",
            "Success",
        )
    else:
        flash("Erro ao apagar registros", "error")

    return redirect(url_for("plantao.pg_plantao"))


@plantao_controller.route("/ajax_disponibilidade_de_vagas", methods=["POST", "GET"])
@login_required()
def ajax_disponibilidade_de_vagas():
    ano = request.args.get("ano")
    mes = request.args.get("mes")

    plantao_service = PlantaoService()
    dias = plantao_service.get_disponibilidade_vagas_mes(
        int(ano), int(mes), current_user.urole
    )

    return current_app.response_class(
        response=json.dumps(dias), status=200, mimetype="application/json"
    )


@plantao_controller.route("/ajax_vagas_disponiveis", methods=["POST", "GET"])
@login_required()
def ajax_vagas_disponiveis():
    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")

    plantao_service = PlantaoService()
    index = plantao_service.get_vagas_disponiveis_data(
        int(ano), int(mes), int(dia), current_user.urole
    )

    return current_app.response_class(
        response=json.dumps(index), status=200, mimetype="application/json"
    )


@plantao_controller.route("/registro_presenca")
@login_required()
def reg_presenca():
    plantao_service = PlantaoService()
    status_data = plantao_service.get_status_presenca_usuario(current_user.id)

    return render_template(
        "plantao/registro_presenca.html",
        data_hora_atual=status_data["data_hora_atual"],
        status_presenca=status_data["status_presenca"],
    )


@plantao_controller.route("/ajax_registra_presenca", methods=["POST"])
@login_required()
def ajax_registra_presenca():
    plantao_service = PlantaoService()
    resposta = plantao_service.registrar_presenca(
        current_user.id, request.json["hora_registrada"]
    )

    return current_app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


@plantao_controller.route("/confirmar_presenca", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.PROFESSOR,
    ]
)
def confirmar_presenca():
    plantao_service = PlantaoService()

    if request.method == "POST":
        dados_cru = request.form.to_dict()
        if not plantao_service.confirmar_presencas(dados_cru):
            flash("Erro ao confirmar presenças", "error")

    presencas_data = plantao_service.get_presencas_para_confirmacao()

    return render_template(
        "plantao/confirmar_presenca.html",
        presencas_registradas=presencas_data["presencas_registradas"],
        plantoes_registradas=presencas_data["plantoes_registradas"],
        data_ontem=presencas_data["data_ontem"],
    )


@plantao_controller.route("/ajax_busca_presencas_data", methods=["POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
        UserRole.PROFESSOR,
    ]
)
def ajax_busca_presencas_data():
    plantao_service = PlantaoService()
    resposta = plantao_service.buscar_presencas_por_data(request.json["nova_data"])

    return current_app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


@plantao_controller.route("/configurar_abertura", methods=["POST", "GET"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
    ]
)
def configurar_abertura():
    plantao_service = PlantaoService()

    form_abrir = AbrirPlantaoForm()
    form_fechar = FecharPlantaoForm()
    _form = SelecionarDuracaoPlantaoForm()

    config_data = plantao_service.get_configuracao_abertura_data()

    if (
        current_user.urole
        not in [
            UserRole.ADMINISTRADOR,
            UserRole.COLAB_PROJETO,
        ]
    ) and (config_data["plantao"] and config_data["plantao"].data_abertura is None):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    from gestaolegal.utils.plantao_utils import (
        set_abrir_plantao_form,
        set_fechar_plantao_form,
    )

    set_abrir_plantao_form(form_abrir, config_data["plantao"])
    set_fechar_plantao_form(form_fechar, config_data["plantao"])

    return render_template(
        "plantao/configurar_plantao.html",
        form_fechar=form_fechar,
        form_abrir=form_abrir,
        periodo=config_data["periodo"],
        form=_form,
        dias_front=config_data["dias_front"],
    )


@plantao_controller.route("/ajax_salva_config_plantao", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.COLAB_PROJETO,
    ]
)
def ajax_salva_config_plantao():
    plantao_service = PlantaoService()

    resposta = plantao_service.salvar_configuracao_plantao(
        datas_duracao=request.json["datas_duracao"],
        data_abertura=request.json["data_abertura"],
        hora_abertura=request.json["hora_abertura"],
        data_fechamento=request.json["data_fechamento"],
        hora_fechamento=request.json["hora_fechamento"],
        user_id=current_user.id,
    )

    return current_app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


@plantao_controller.route("/fila-atendimento", methods=["GET", "POST"])
@login_required()
def fila_atendimento():
    return render_template("plantao/fila_atendimento.html")


@plantao_controller.route("/fila-atendimento/criar", methods=["GET", "POST"])
@login_required()
def criar_fila():
    if request.method == "GET":
        return json.dumps({"error": "error to access the page"})

    plantao_service = PlantaoService()
    data = request.get_json(silent=True, force=True)
    resultado = plantao_service.criar_fila_atendimento(data)

    return json.dumps(resultado)


@plantao_controller.route("/fila-atendimento/hoje", methods=["GET", "PUT"])
@login_required()
def pegar_atendimentos():
    logger.info("Entering pegar_atendimentos route")
    plantao_service = PlantaoService()

    if request.method == "PUT":
        data = request.get_json(silent=True, force=True)
        resultado = plantao_service.atualizar_status_fila(data["id"], data["status"])
        return json.dumps(resultado)

    fila_obj = plantao_service.get_atendimentos_hoje()
    return json.dumps(fila_obj)


@plantao_controller.route("/atendido/fila-atendimento", methods=["GET", "POST"])
@login_required()
def ajax_cadastrar_atendido():
    try:
        logger.info("Entering ajax_cadastrar_atendido route")
        atendido_service = AtendidoService()
        data = request.get_json(silent=True, force=True)

        logger.info(f"Received data keys: {list(data.keys()) if data else 'None'}")
        logger.debug(f"Full received data: {data}")

        if not data:
            logger.warning("No data received in ajax_cadastrar_atendido")
            return json.dumps({"message": "error: No data received"})

        logger.info("Calling create_atendido_from_json...")
        resultado = atendido_service.create_atendido_from_json(data)
        logger.info(f"Result from create_atendido_from_json: {resultado}")

        return json.dumps(resultado)
    except Exception as e:
        logger.error(f"Error in ajax_cadastrar_atendido: {str(e)}", exc_info=True)
        return json.dumps({"message": f"error: {str(e)}"})
