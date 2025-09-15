import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.usuario import (
    CadastrarUsuarioForm,
    EditarSenhaForm,
    EditarUsuarioForm,
)
from gestaolegal.repositories.base_repository import PageParams
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.decorators import login_required

logger = logging.getLogger(__name__)

usuario_controller = Blueprint(
    "usuario", __name__, template_folder="../../static/templates"
)


@usuario_controller.route("/me", methods=["GET"])
@login_required()
def meu_perfil():
    usuario_service = UsuarioService()
    entidade_usuario = usuario_service.find_by_id(current_user.id)

    return render_template(
        "usuarios/visualizar_perfil.html",
        usuario=entidade_usuario,
    )


@usuario_controller.route("/<int:id_user>", methods=["GET"])
@login_required()
def perfil_usuario(id_user):
    usuario_service = UsuarioService()
    entidade_usuario = usuario_service.find_by_id(id_user)
    if not entidade_usuario:
        abort(404)
    entidade_endereco = entidade_usuario.endereco
    return render_template(
        "usuarios/visualizar_perfil.html",
        usuario=entidade_usuario,
        endereco=entidade_endereco,
    )


@usuario_controller.route("/editar/<int:id_user>", methods=["POST", "GET"])
@login_required()
def editar_usuario(id_user):
    usuario_service = UsuarioService()

    if request.method == "POST":
        try:
            form = EditarUsuarioForm()
            user_data = form.to_dict()

            usuario_service.update(
                user_id=id_user,
                user_data=user_data,
                modificado_por=current_user.id,
            )

            flash("Usuário alterado com sucesso!", "success")
            return redirect(url_for("usuario.perfil_usuario", id_user=id_user))

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}", exc_info=True)
            flash("Erro ao editar usuário. Tente novamente.", "error")
            return redirect(url_for("principal.index"))

    usuario = usuario_service.find_by_id(id_user)
    form = EditarUsuarioForm(data=usuario.to_dict(inline_other_models=True))

    return render_template(
        "usuarios/formularios/editar_usuario.html",
        form=form,
        entidade_usuario=usuario,
        id_user=id_user,
        id_usuario_logado=current_user.id,
        id_usuario_padrao=current_app.config["ADMIN_PADRAO"],
    )


@usuario_controller.route("/editar_senha", methods=["POST", "GET"])
@login_required()
def editar_senha_usuario():
    usuario_service = UsuarioService()
    form = EditarSenhaForm()

    if request.method == "POST":
        try:
            new_password = form.to_dict()["senha"]
            result = usuario_service.update_password(
                user_id=current_user.id,
                new_password=new_password,
                from_admin=False,
            )

            if result:
                flash("Senha alterada com sucesso!", "success")
                return redirect(url_for("principal.index"))

        except Exception as e:
            logger.error(f"Error updating password: {str(e)}", exc_info=True)
            flash("Erro ao alterar senha. Tente novamente.", "error")
            return redirect(url_for("principal.index"))

    return render_template("usuarios/formularios/editar_senha.html", form=form)


@usuario_controller.route("/cadastrar", methods=["POST", "GET"])
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def cadastrar_usuario():
    logger.info("Entering cadastrar_usuario route")
    usuario_service = UsuarioService()
    form = CadastrarUsuarioForm()

    if request.method == "POST":
        user_data = form.to_dict()
        result = usuario_service.create(user_data=user_data, criado_por=current_user.id)

        flash("Usuário cadastrado!", "success")
        return redirect(url_for("usuario.perfil_usuario", id_user=result.id))

    return render_template("usuarios/formularios/cadastrar_usuario.html", form=form)


@usuario_controller.route("/login", methods=["POST", "GET"])
def login():
    logger.info("Entering login route - Login attempt initiated")
    usuario_service = UsuarioService()

    if request.method == "POST":
        try:
            usuario = usuario_service.process_login(
                login=request.form.get("login"), senha=request.form.get("senha")
            )
            login_user(usuario)
            logger.info(f"User {usuario.email} logged in successfully")
            flash("Você foi logado com sucesso!", "success")
            return redirect(url_for("principal.index"))
        except ValueError as e:
            logger.warning(f"Failed login attempt: {str(e)}")
            flash(str(e), "warning")
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            flash("Erro interno do servidor", "error")

    return render_template("autenticacao/entrar.html")


@usuario_controller.route("/logout")
def logout():
    logger.info("Entering logout route")
    if current_user:
        flash("Logout feito com sucesso!", "info")
        logout_user()
    else:
        flash("Você precisa estar logado para continuar", "info")
    return redirect(url_for("usuario.login"))


@usuario_controller.route("/")
@login_required()
def listar_usuarios():
    usuario_service = UsuarioService()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    if search or funcao != "all" or status != "1":
        usuarios = usuario_service.search_users_by_filters(
            search,
            funcao,
            status,
            page_params=PageParams(
                page=page, per_page=current_app.config["USUARIOS_POR_PAGINA"]
            ),
        )
    else:
        usuarios = usuario_service.get_all(
            page_params=PageParams(
                page=page, per_page=current_app.config["USUARIOS_POR_PAGINA"]
            )
        )

    return render_template(
        "usuarios/listagem_usuarios.html",
        usuarios=usuarios,
        admin_padrao=current_app.config["ADMIN_PADRAO"],
        UserRole=UserRole,
        search=search,
        funcao=funcao,
        status=status,
    )


@usuario_controller.route("/inativar/", methods=["POST", "GET"])
@login_required(role=UserRole.ADMINISTRADOR)
def excluir_usuario():
    usuario_service = UsuarioService()

    if request.method == "POST":
        try:
            form = request.form
            form_id = form["id"]

            if int(form_id) == current_user.id:
                flash("Você não tem permissão para executar esta ação.", "warning")
                return redirect(url_for("principal.index"))

            if int(form_id) == current_app.config["ADMIN_PADRAO"]:
                flash("O administrador padrão não pode ser inativado.", "warning")
                return redirect(url_for("principal.index"))

            if usuario_service.soft_delete(int(form_id)):
                flash("Usuário inativado.", "Success")
            else:
                flash("Usuário não encontrado.", "error")
        except Exception:
            flash(
                "Erro ao processar a solicitação. Por favor, tente novamente.", "error"
            )
            return redirect(url_for("usuario.listar_usuarios"))
    return redirect(url_for("principal.index"))


@usuario_controller.route("/mudar_senha_admin", methods=["POST"])
@login_required(role=UserRole.ADMINISTRADOR)
def muda_senha_admin():
    id_usuario = request.form["id"]

    return render_template(
        "autenticacao/definir_nova_senha.html", id_usuario=id_usuario
    )


@usuario_controller.route("/confirmar_senha", methods=["POST"])
@login_required(role=UserRole.ADMINISTRADOR)
def confirma_senha():
    usuario_service = UsuarioService()
    id_usuario = int(request.form["id_usuario"])
    senha = request.form["senha"]
    confirmar_senha = request.form["confirmar_senha"]

    is_valid, error_message = usuario_service.validate_password(senha)
    if not is_valid:
        flash(error_message, "warning")
        return render_template(
            "autenticacao/definir_nova_senha.html", id_usuario=id_usuario
        )

    if senha != confirmar_senha:
        flash("As senhas não são iguais", "warning")
        return redirect(url_for("usuario.listar_usuarios"))

    if usuario_service.update_password(id_usuario, senha, from_admin=True):
        flash("Sua senha foi alterada com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")

    return redirect(url_for("usuario.listar_usuarios"))


@usuario_controller.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    usuario_service = UsuarioService()

    if request.method == "POST":
        data = request.get_json(silent=True, force=True)
        try:
            usuario_service.process_password_recovery(data["email"])
            return json.dumps(
                {"success": True, "message": "Email de recuperação enviado com sucesso"}
            )
        except ValueError as e:
            return json.dumps({"success": False, "message": str(e)})

    return render_template("autenticacao/recuperar_senha.html")


@usuario_controller.route("/resetar_senha/<token>", methods=["GET", "POST"])
def resetar_senha(token):
    usuario_service = UsuarioService()

    if request.method == "POST":
        data = request.get_json(silent=True, force=True)
        try:
            usuario_service.reset_password_with_token(token, data["password"])
            return json.dumps(
                {"success": True, "message": "Senha alterada com sucesso"}
            )
        except ValueError as e:
            return json.dumps({"success": False, "message": str(e)})

    # GET request - validate token
    try:
        usuario_service.validate_password_reset_token(token)
    except ValueError as e:
        flash(str(e), "warning")
        return redirect(url_for("usuario.login"))
    except Exception:
        flash("Token inválido", "warning")
        return redirect(url_for("usuario.login"))

    return render_template("autenticacao/redefinir_senha.html")
