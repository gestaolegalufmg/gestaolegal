from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    json,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from flask_mail import Message

from gestaolegal import mail
from gestaolegal.common.constants import UserRole
from gestaolegal.database import get_db
from gestaolegal.forms.usuario import CadastrarUsuarioForm, EditarUsuarioForm
from gestaolegal.models.usuario import Usuario
from gestaolegal.services.usuario_service import UsuarioService
from gestaolegal.utils.decorators import login_required

usuario_controller = Blueprint(
    "usuario", __name__, template_folder="../static/templates"
)


@usuario_controller.route("/relatorio", methods=["GET", "POST"])
def relatorio():
    return render_template("sistema/pagina_relatorios.html")


@usuario_controller.route("/arquivo", methods=["GET", "POST"])
def arquivo():
    return render_template("sistema/pagina_arquivos.html")


@usuario_controller.route("/plantao", methods=["GET", "POST"])
def plantao():
    return render_template("sistema/pagina_plantao.html")


@usuario_controller.route("/casos_id", methods=["GET", "POST"])
def casos_esp():
    return render_template("sistema/meus_casos.html")


@usuario_controller.route("/meu_perfil", methods=["GET"])
@login_required()
def meu_perfil():
    usuario_service = UsuarioService()
    entidade_usuario = usuario_service.find_by_id(current_user.id)
    if not entidade_usuario:
        abort(404)
    entidade_endereco = entidade_usuario.endereco
    return render_template(
        "usuarios/visualizar_perfil.html",
        usuario=entidade_usuario,
        endereco=entidade_endereco,
    )


@usuario_controller.route("/perfil/<int:id_user>", methods=["GET"])
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


@usuario_controller.route("/editar_usuario/<int:id_user>", methods=["POST", "GET"])
@login_required()
def editar_usuario(id_user):
    usuario_service = UsuarioService()

    def renderizaTemplate(
        form: EditarUsuarioForm,
        entidade_usuario: Usuario,
        id_user: int,
        id_usuario_logado: int,
        id_usuario_padrao: int,
    ):
        return render_template(
            "usuarios/formularios/editar_usuario.html",
            form=form,
            entidade_usuario=entidade_usuario,
            id_user=id_user,
            id_usuario_logado=id_usuario_logado,
            id_usuario_padrao=id_usuario_padrao,
        )

    form = EditarUsuarioForm()

    if id_user > 0:
        if (
            current_user.urole
            not in [
                UserRole.ADMINISTRADOR,
                UserRole.PROFESSOR,
            ]
        ) and (current_user.id != id_user):
            flash("Você não tem permissão para editar outro usuário.", "warning")
            return redirect(url_for("principal.index"))
        entidade_usuario = usuario_service.find_by_id_with_inactive(id_user)
    else:
        entidade_usuario = usuario_service.find_by_id_with_inactive(current_user.id)

    if not entidade_usuario:
        flash("Usuário não encontrado.", "warning")
        return redirect(url_for("principal.index"))

    is_valid, error_message = usuario_service.validate_user_permissions(
        entidade_usuario.id,
        current_user.id,
        current_user.urole,
        current_app.config["ADMIN_PADRAO"],
    )
    if not is_valid:
        flash(error_message, "warning")
        return redirect(url_for("principal.index"))

    is_valid, error_message = usuario_service.validate_user_status(entidade_usuario.id)
    if not is_valid:
        flash(error_message, "warning")
        return redirect(url_for("principal.index"))

    if request.method == "POST":
        if entidade_usuario.id == current_app.config["ADMIN_PADRAO"]:
            form.urole.data = UserRole.ADMINISTRADOR

        if not usuario_service.validate_email_unique(
            form.email.data, request.form["emailAtual"]
        ):
            flash("Este email já existe!", "warning")
            return renderizaTemplate(
                form,
                entidade_usuario,
                id_user,
                current_user.id,
                current_app.config["ADMIN_PADRAO"],
            )

        if not form.validate():
            return renderizaTemplate(
                form,
                entidade_usuario,
                id_user,
                current_user.id,
                current_app.config["ADMIN_PADRAO"],
            )

        updated_user = usuario_service.update_user_from_form(
            entidade_usuario.id, form, current_user.get_id()
        )

        if updated_user:
            flash("Usuário alterado com sucesso!", "success")
            return redirect(
                url_for("usuario.perfil_usuario", id_user=entidade_usuario.id)
            )
        else:
            flash("Erro ao atualizar usuário.", "error")
            return renderizaTemplate(
                form,
                entidade_usuario,
                id_user,
                current_user.id,
                current_app.config["ADMIN_PADRAO"],
            )

    EditarUsuarioForm.from_model(form, entidade_usuario)

    return renderizaTemplate(
        form,
        entidade_usuario,
        id_user,
        current_user.id,
        current_app.config["ADMIN_PADRAO"],
    )


@usuario_controller.route("/editar_senha_usuario", methods=["POST", "GET"])
@login_required()
def editar_senha_usuario():
    usuario_service = UsuarioService()

    if request.method == "POST":
        form = request.form
        confirmacao = form["confirmacao"]
        senha = form["senha"]

        is_valid, error_message = usuario_service.validate_password(senha)
        if not is_valid:
            flash(error_message, "warning")
            return render_template("usuarios/formularios/alterar_senha.html")

        if confirmacao != senha:
            flash("Confirmação de senha e senha estão diferentes.", "warning")
            return render_template("usuarios/formularios/alterar_senha.html")

        if usuario_service.update_password(current_user.id, senha):
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("principal.index"))
        else:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for("principal.index"))

    return render_template("usuarios/formularios/alterar_senha.html")


@usuario_controller.route("/cadastrar_usuario", methods=["POST", "GET"])
@login_required(role=[UserRole.ADMINISTRADOR, UserRole.PROFESSOR])
def cadastrar_usuario():
    usuario_service = UsuarioService()
    form = CadastrarUsuarioForm()

    if request.method == "POST":
        is_valid, error_message = usuario_service.validate_password(form.senha.data)
        if not is_valid:
            flash(error_message, "warning")
            return render_template(
                "usuarios/formularios/cadastrar_usuario.html", form=form
            )

        if form.confirmacao.data != form.senha.data:
            flash("Confirmação de senha e senha estão diferentes.", "warning")
            return render_template(
                "usuarios/formularios/cadastrar_usuario.html", form=form
            )

        if not usuario_service.validate_email_unique(form.email.data):
            flash("Este email já está em uso.", "warning")
            return render_template(
                "usuarios/formularios/cadastrar_usuario.html", form=form
            )

        if not form.validate():
            return render_template(
                "usuarios/formularios/cadastrar_usuario.html", form=form
            )

        entidade_usuario = usuario_service.create_user_from_form(
            form, current_user.get_id()
        )

        flash("Usuário cadastrado!", "success")
        return redirect(url_for("usuario.perfil_usuario", id_user=entidade_usuario.id))

    return render_template("usuarios/formularios/cadastrar_usuario.html", form=form)


@usuario_controller.route("/login", methods=["POST", "GET"])
def login():
    usuario_service = UsuarioService()

    if request.method == "POST":
        form = request.form
        login = form["login"]
        senha = form["senha"]

        loginUsuario = usuario_service.authenticate_user(login, senha)
        if loginUsuario:
            login_user(loginUsuario)
            flash("Você foi logado com sucesso!", "success")
            return redirect(url_for("principal.index"))
        else:
            if usuario_service.find_by_email_with_inactive(login):
                flash("Senha inválida!", "warning")
            else:
                flash("Email inválido!", "warning")

    return render_template("autenticacao/entrar.html")


@usuario_controller.route("/logout")
def logout():
    if current_user:
        flash("Logout feito com sucesso!", "info")
        logout_user()
    else:
        flash("Você precisa estar logado para continuar", "info")
    return redirect(url_for("usuario.login"))


@usuario_controller.route("/listar_usuarios")
@login_required()
def listar_usuarios():
    db = get_db()
    usuario_service = UsuarioService()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    def paginator(query):
        return db.paginate(
            query,
            page=page,
            per_page=current_app.config["USUARIOS_POR_PAGINA"],
            error_out=False,
        )

    if search or funcao != "all" or status != "1":
        usuarios = usuario_service.search_users_by_filters(
            search, funcao, status, paginator
        )
    else:
        usuarios = usuario_service.get_all(paginator)

    return render_template(
        "usuarios/listagem_usuarios.html",
        usuarios=usuarios,
        admin_padrao=current_app.config["ADMIN_PADRAO"],
        UserRole=UserRole,
        search=search,
        funcao=funcao,
        status=status,
    )


@usuario_controller.route("/busca_usuarios_ajax", methods=["GET"])
@login_required()
def busca_usuarios_ajax():
    db = get_db()
    usuario_service = UsuarioService()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    def paginator(query):
        return db.paginate(
            query,
            page=page,
            per_page=current_app.config["USUARIOS_POR_PAGINA"],
            error_out=False,
        )

    if search or funcao != "all" or status != "1":
        usuarios = usuario_service.search_users_by_filters(
            search, funcao, status, paginator
        )
    else:
        usuarios = usuario_service.get_all(paginator)

    table_html = render_template(
        "usuarios/parciais/linhas_tabela_usuarios.html",
        usuarios=usuarios,
        admin_padrao=current_app.config["ADMIN_PADRAO"],
        UserRole=UserRole,
    )

    pagination_html = (
        render_template(
            "usuarios/parciais/paginacao_usuarios.html",
            usuarios=usuarios,
        )
        if usuarios.pages > 1
        else ""
    )

    return jsonify(
        {
            "success": True,
            "table_html": table_html,
            "pagination_html": pagination_html,
            "total": usuarios.total,
            "page": usuarios.page,
            "pages": usuarios.pages,
        }
    )


@usuario_controller.route("/busca_usuarios", methods=["GET"])
@login_required()
def busca_usuarios():
    usuario_service = UsuarioService()
    valor_busca = request.args.get("valor_busca", "")
    funcao = request.args.get("funcao", "all")
    status = request.args.get("status", "1")

    usuarios = usuario_service.search_users_by_filters(valor_busca, funcao, status)
    return jsonify({"users": [x.as_dict() for x in usuarios]})


@usuario_controller.route("/inativar_usuario_lista/", methods=["POST", "GET"])
@login_required(role=UserRole.ADMINISTRADOR)
def inativar_usuario_lista():
    usuario_service = UsuarioService()

    if request.method == "POST":
        try:
            form = request.form
            form_id = form["id"]

            if int(form_id) == current_user.get_id():
                flash("Você não tem permissão para executar esta ação.", "warning")
                return redirect(url_for("principal.index"))

            if int(form_id) == current_app.config["ADMIN_PADRAO"]:
                flash("O administrador padrão não pode ser inativado.", "warning")
                return redirect(url_for("principal.index"))

            if usuario_service.deactivate_user(int(form_id)):
                flash("Usuário inativado.", "Success")
            else:
                flash("Usuário não encontrado.", "error")
        except Exception:
            flash(
                "Erro ao processar a solicitação. Por favor, tente novamente.", "error"
            )
            return redirect(url_for("usuario.listar_usuarios"))
    return redirect(url_for("principal.index"))


@usuario_controller.route("/muda_senha_admin", methods=["POST"])
@login_required(role=UserRole.ADMINISTRADOR)
def muda_senha_admin():
    id_usuario = request.form["id"]

    return render_template(
        "autenticacao/definir_nova_senha.html", id_usuario=id_usuario
    )


@usuario_controller.route("/confirma_senha", methods=["POST"])
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

    if usuario_service.update_password_admin(id_usuario, senha):
        flash("Sua senha foi alterada com sucesso.", "success")
    else:
        flash("Usuário não encontrado.", "error")

    return redirect(url_for("usuario.listar_usuarios"))


@usuario_controller.route("/listar_usuarios_ajax/", methods=["GET"])
@login_required()
def lista_usuario_ajax():
    usuario_service = UsuarioService()

    funcao = request.args.get("funcao")
    status = request.args.get("status")

    usuarios = usuario_service.get_users_by_filters_ajax(funcao, status)
    return jsonify({"users": [x.as_dict() for x in usuarios]})


@usuario_controller.route("/esqueci-a-senha", methods=["GET", "POST"])
def esqueci_senha():
    usuario_service = UsuarioService()

    if request.method == "POST":
        data = request.get_json(silent=True, force=True)
        email = data["email"]

        usuario = usuario_service.find_by_email_with_inactive(email)
        if not usuario:
            return json.dumps({"status": "error", "message": "E-mail não existe"})

        if usuario_service.set_password_recovery(email):
            titulo = "Recuperação de senha Gestão Legal"
            token = usuario.tokenRecuperacao()
            msg = Message(
                titulo,
                sender=current_app.config["MAIL_USERNAME"],
                recipients=[usuario.email],
            )
            msg.body = f""" Solicitação de recuperação/alteração de senha.

            Se você solicitou este serviço, por favor, clique no link abaixo:
            {url_for("usuario.resetar_senha", token=token, _external=True)}

            Caso você não tenha solicitado este serviço, por favor ignore essa mensagem.
            """
            mail.send(msg)
            return json.dumps(
                {
                    "status": "success",
                    "user": {"nome": usuario.nome, "email": usuario.email},
                }
            )

    return render_template("autenticacao/recuperar_senha.html")


@usuario_controller.route("/resetar-a-senha/<token>", methods=["GET", "POST"])
def resetar_senha(token):
    usuario_service = UsuarioService()

    usuario = Usuario.verificaToken(token)
    if usuario is None:
        flash("Token inválido.", "warning")
        return redirect(url_for("usuario.login"))

    if usuario.chave_recuperacao:
        if request.method == "POST":
            data = request.get_json(silent=True, force=True)
            if usuario_service.reset_password_with_token(token, data["password"]):
                return json.dumps({"status": "success"})
            else:
                return json.dumps(
                    {"status": "error", "message": "Erro ao resetar senha"}
                )
    else:
        flash("Erro! Por favor refaça a operação", "warning")
        return redirect(url_for("usuario.login"))

    return render_template("autenticacao/redefinir_senha.html")
