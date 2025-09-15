import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.arquivo import ArquivoForm
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.services.arquivo_service import ArquivoService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

arquivo_controller = Blueprint(
    "arquivos", __name__, template_folder="../../static/templates"
)


@arquivo_controller.route("/")
@login_required()
def index():
    arquivo_service = ArquivoService()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()

    result = arquivo_service.get(
        search,
        page_params=PageParams(
            page=page, per_page=current_app.config["ARQUIVOS_POR_PAGINA"]
        ),
    )

    return render_template(
        "arquivos/listagem_arquivos.html", arquivos=result, search=search
    )


@arquivo_controller.route("/cadastrar_arquivo", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def cadastrar_arquivo():
    try:
        arquivo_service = ArquivoService()
        _form = ArquivoForm()

        if request.method == "POST":
            arquivo_service.create(_form.to_dict(), request.files["arquivo"])

            flash("Arquivo adicionado", "success")
            return redirect(url_for("arquivos.index"))

    except Exception as e:
        logger.error(f"Error in cadastrar_arquivo: {str(e)}", exc_info=True)
        flash(str(e), "error")

    return render_template("arquivos/cadastrar_arquivo.html", form=_form)


@arquivo_controller.route("/editar_arquivo/<int:id>", methods=["GET", "POST"])
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
        UserRole.COLAB_EXTERNO,
    ]
)
def editar_arquivo(id):
    arquivo_service = ArquivoService()

    if request.method == "POST":
        result = arquivo_service.update(id=id, form=request.form, request=request)

        if result:
            flash("Arquivo editado com sucesso.", "success")
            return redirect(url_for("arquivos.visualizar_arquivo", id=id))

    arquivo = arquivo_service.find_by_id(id)

    if not arquivo:
        abort(404)

    arquivo_data = arquivo.to_dict()
    arquivo_data.pop("blob", None)

    form = ArquivoForm(data=arquivo_data)
    return render_template(
        "arquivos/editar_arquivo.html",
        form=form,
        arquivo=arquivo_data,
    )


@arquivo_controller.route("/visualizar_arquivo/<int:id>")
@login_required()
def visualizar_arquivo(id):
    arquivo_service = ArquivoService()

    arquivo = arquivo_service.find_by_id(id)
    if not arquivo:
        abort(404)

    return render_template("arquivos/visualizar_arquivo.html", arquivo=arquivo)


@arquivo_controller.route("/excluir_arquivo/<int:id>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
    ]
)
def excluir_arquivo(id):
    arquivo_service = ArquivoService()

    arquivo_service.delete(id)

    flash("Arquivo excluido.", "success")
    return redirect(url_for("arquivos.index"))
