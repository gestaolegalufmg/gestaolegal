from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from gestaolegal import db, login_required
from gestaolegal.plantao.forms import CadastroAtendidoForm
from gestaolegal.plantao.models import Atendido
from gestaolegal.plantao.views_util import setValoresFormAtendido
from gestaolegal.usuario.models import Endereco, usuario_urole_roles

atendido_controller = Blueprint("atendido", __name__)


def valida_dados_form(form: CadastroAtendidoForm):
    email_repetido = db.session.query(Atendido).filter_by(email=form.email.data).first()

    if not form.validate():
        return False
    return True


def cria_atendido(form: CadastroAtendidoForm):
    entidade_endereco = Endereco(
        logradouro=form.logradouro.data,
        numero=form.numero.data,
        complemento=form.complemento.data,
        bairro=form.bairro.data,
        cep=form.cep.data,
        cidade=form.cidade.data,
        estado=form.estado.data,
    )
    db.session.add(entidade_endereco)
    db.session.flush()

    entidade_atendido = Atendido(
        nome=form.nome.data,
        data_nascimento=form.data_nascimento.data,
        cpf=form.cpf.data,
        cnpj=form.cnpj.data,
        telefone=form.telefone.data,
        celular=form.celular.data,
        email=form.email.data,
        estado_civil=form.estado_civil.data,
        como_conheceu=form.como_conheceu.data,
        indicacao_orgao=form.indicacao_orgao.data,
        procurou_outro_local=form.procurou_outro_local.data,
        procurou_qual_local=form.procurou_qual_local.data,
        obs=form.obs_atendido.data,
        endereco_id=entidade_endereco.id,
        pj_constituida=form.pj_constituida.data,
        repres_legal=form.repres_legal.data,
        nome_repres_legal=form.nome_repres_legal.data,
        cpf_repres_legal=form.cpf_repres_legal.data,
        contato_repres_legal=form.contato_repres_legal.data,
        rg_repres_legal=form.rg_repres_legal.data,
        nascimento_repres_legal=form.nascimento_repres_legal.data,
        pretende_constituir_pj=form.pretende_constituir_pj.data,
        status=1,
    )

    entidade_atendido.setIndicacao_orgao(
        form.indicacao_orgao.data, entidade_atendido.como_conheceu
    )
    entidade_atendido.setCnpj(
        entidade_atendido.pj_constituida, form.cnpj.data, form.repres_legal.data
    )
    entidade_atendido.setRepres_legal(
        entidade_atendido.repres_legal,
        entidade_atendido.pj_constituida,
        form.nome_repres_legal.data,
        form.cpf_repres_legal.data,
        form.contato_repres_legal.data,
        form.rg_repres_legal.data,
        form.nascimento_repres_legal.data,
    )
    entidade_atendido.setProcurou_qual_local(
        entidade_atendido.procurou_outro_local, form.procurou_qual_local.data
    )

    return entidade_atendido


@atendido_controller.route("/novo_atendimento", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_na():
    form = CadastroAtendidoForm()

    if request.method == "POST":
        if not valida_dados_form(form):
            return render_template("cadastro_novo_atendido.html", form=form)

        db.session.add(cria_atendido(form))
        db.session.commit()

        flash("Atendido cadastrado!", "success")
        _id = db.session.query(Atendido).filter_by(email=form.email.data).first().id
        return redirect(url_for("plantao.perfil_assistido", _id=_id))

    return render_template("cadastro_novo_atendido.html", form=form)


@atendido_controller.route("/dados_atendido/<int:id>", methods=["GET"])
@login_required()
def dados_atendido(id):
    _atendido = db.session.get(Atendido, id)
    if not _atendido:
        abort(404)
    _form = CadastroAtendidoForm()
    setValoresFormAtendido(_atendido, _form)
    _form.id_atendido = _atendido.id
    return render_template("dados_atendido.html", form=_form)


@atendido_controller.route("/excluir_atendido/", methods=["POST", "GET"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_atendido():
    id_atendido = request.form.get("id_atendido")
    atendido = db.session.get(Atendido, id_atendido)
    if not atendido:
        abort(404)
    atendido.status = False
    db.session.commit()
    flash("Atendido excluído com sucesso!", "success")
    return redirect(url_for("plantao.listar_atendidos"))


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def editar_atendido(id_atendido):
    atendido = db.session.get(Atendido, id_atendido)
    if not atendido:
        abort(404)
    form = CadastroAtendidoForm()

    if request.method == "POST":
        if form.validate():
            atendido.nome = form.nome.data
            atendido.data_nascimento = form.data_nascimento.data
            atendido.cpf = form.cpf.data
            atendido.cnpj = form.cnpj.data
            atendido.telefone = form.telefone.data
            atendido.celular = form.celular.data
            atendido.email = form.email.data
            atendido.estado_civil = form.estado_civil.data
            atendido.como_conheceu = form.como_conheceu.data
            atendido.indicacao_orgao = form.indicacao_orgao.data
            atendido.procurou_outro_local = form.procurou_outro_local.data
            atendido.procurou_qual_local = form.procurou_qual_local.data
            atendido.obs = form.obs_atendido.data
            atendido.pj_constituida = form.pj_constituida.data
            atendido.repres_legal = form.repres_legal.data
            atendido.nome_repres_legal = form.nome_repres_legal.data
            atendido.cpf_repres_legal = form.cpf_repres_legal.data
            atendido.contato_repres_legal = form.contato_repres_legal.data
            atendido.rg_repres_legal = form.rg_repres_legal.data
            atendido.nascimento_repres_legal = form.nascimento_repres_legal.data
            atendido.pretende_constituir_pj = form.pretende_constituir_pj.data

            atendido.endereco.logradouro = form.logradouro.data
            atendido.endereco.numero = form.numero.data
            atendido.endereco.complemento = form.complemento.data
            atendido.endereco.bairro = form.bairro.data
            atendido.endereco.cep = form.cep.data
            atendido.endereco.cidade = form.cidade.data
            atendido.endereco.estado = form.estado.data

            db.session.commit()
            flash("Atendido editado com sucesso!", "success")
            return redirect(url_for("plantao.perfil_assistido", _id=atendido.id))

    setValoresFormAtendido(atendido, form)
    return render_template("editar_atendido.html", form=form)
