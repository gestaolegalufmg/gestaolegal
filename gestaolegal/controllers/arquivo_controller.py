import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from gestaolegal.common.constants import UserRole
from gestaolegal.database import get_db
from gestaolegal.forms.arquivo import ArquivoForm
from gestaolegal.models.arquivo import Arquivo
from gestaolegal.schemas.arquivo import ArquivoSchema
from gestaolegal.utils.decorators import login_required

arquivo_controller = Blueprint(
    "arquivos", __name__, template_folder="../static/templates"
)


@arquivo_controller.route("/")
@login_required()
def index():
    db = get_db()

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    
    arquivos_schema = db.session.query(ArquivoSchema)
    
    if search:
        arquivos_schema = arquivos_schema.filter(ArquivoSchema.titulo.ilike(f"%{search}%"))
    
    arquivos_schema = db.paginate(
        arquivos_schema,
        page=page,
        per_page=current_app.config["ARQUIVOS_POR_PAGINA"],
        error_out=False,
    )

    arquivos_schema.items = [
        Arquivo.from_sqlalchemy(item) for item in arquivos_schema.items
    ]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from flask_login import current_user
        can_edit = current_user.urole in [
            UserRole.ADMINISTRADOR.value, 
            UserRole.COLAB_PROJETO.value, 
            UserRole.COLAB_EXTERNO.value, 
            UserRole.PROFESSOR.value
        ]
        
        return jsonify({
            'items': [
                {
                    'id': arquivo.id,
                    'titulo': arquivo.titulo,
                    'visualizar_url': url_for('arquivos.visualizar_arquivo', id=arquivo.id),
                    'editar_url': url_for('arquivos.editar_arquivo', id=arquivo.id),
                    'excluir_url': url_for('arquivos.excluir_arquivo', id=arquivo.id)
                } for arquivo in arquivos_schema.items
            ],
            'total': arquivos_schema.total,
            'page': arquivos_schema.page,
            'pages': arquivos_schema.pages,
            'has_prev': arquivos_schema.has_prev,
            'has_next': arquivos_schema.has_next,
            'prev_num': arquivos_schema.prev_num,
            'next_num': arquivos_schema.next_num,
            'first_item': arquivos_schema.first_item,
            'last_item': arquivos_schema.last_item,
            'can_edit': can_edit
        })
    
    return render_template("arquivos/listagem_arquivos.html", arquivos=arquivos_schema, search=search)


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
    db = get_db()
    _form = ArquivoForm()
    if _form.validate_on_submit():
        arquivo = request.files.get(_form.arquivo.name)
        if not arquivo or arquivo.filename == "":
            flash("Você precisa adicionar um arquivo.", "warning")
            return redirect(url_for("arquivos.cadastrar_arquivo"))
        # Ensure the arquivos directory exists
        arquivos_dir = os.path.join(current_app.root_path, "static", "arquivos")
        os.makedirs(arquivos_dir, exist_ok=True)

        _arquivo_schema = ArquivoSchema(
            titulo=_form.titulo.data,
            descricao=_form.descricao.data,
            nome=arquivo.filename,
        )
        arquivo.save(os.path.join(arquivos_dir, arquivo.filename))
        db.session.add(_arquivo_schema)
        db.session.commit()
        flash("Arquivo adicionado", "success")
        return redirect(url_for("arquivos.index"))

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
    db = get_db()

    _arquivo_schema = db.session.get(ArquivoSchema, id)
    if not _arquivo_schema:
        abort(404)

    _form = ArquivoForm()

    if _form.validate_on_submit():
        arquivo = request.files.get(_form.arquivo.name)
        _arquivo_schema.titulo = _form.titulo.data
        _arquivo_schema.descricao = _form.descricao.data

        if arquivo.filename:
            local_arquivo = os.path.join(
                current_app.root_path, "static", "arquivos", _arquivo_schema.nome
            )
            if os.path.exists(local_arquivo):
                os.remove(local_arquivo)

            _arquivo_schema.nome = arquivo.filename
            arquivo.save(
                os.path.join(
                    current_app.root_path, "static", "arquivos", arquivo.filename
                )
            )

        db.session.commit()
        flash("Arquivo editado", "success")
        return redirect(url_for("arquivos.visualizar_arquivo", id=id))

    _form.titulo.data = _arquivo_schema.titulo
    _form.descricao.data = _arquivo_schema.descricao

    _arquivo = Arquivo.from_sqlalchemy(_arquivo_schema)
    return render_template("arquivos/editar_arquivo.html", form=_form, arquivo=_arquivo)


@arquivo_controller.route("/visualizar_arquivo/<int:id>")
@login_required()
def visualizar_arquivo(id):
    db = get_db()

    _arquivo_schema = db.session.get(ArquivoSchema, id)
    if not _arquivo_schema:
        abort(404)

    _arquivo = Arquivo.from_sqlalchemy(_arquivo_schema)
    return render_template("arquivos/visualizar_arquivo.html", arquivo=_arquivo)


@arquivo_controller.route("/excluir_arquivo/<int:id>")
@login_required(
    role=[
        UserRole.ADMINISTRADOR,
        UserRole.PROFESSOR,
        UserRole.COLAB_PROJETO,
    ]
)
def excluir_arquivo(id):
    db = get_db()

    _arquivo_schema = db.session.get(ArquivoSchema, id)
    if not _arquivo_schema:
        abort(404)

    local_arquivo = os.path.join(
        current_app.root_path, "static", "arquivos", _arquivo_schema.nome
    )

    if os.path.exists(local_arquivo):
        os.remove(local_arquivo)

    db.session.delete(_arquivo_schema)
    db.session.commit()

    flash("arquivo excluido.")

    return redirect(url_for("arquivos.index"))
