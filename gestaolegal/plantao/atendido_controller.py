from typing import cast

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from gestaolegal import app, db, login_required
from gestaolegal.plantao.forms.cadastro_atendido_form import CadastroAtendidoForm
from gestaolegal.plantao.forms.tornar_assistido_form import TornarAssistidoForm
from gestaolegal.plantao.models import (
    Assistido,
    AssistidoPessoaJuridica,
    Atendido,
)
from gestaolegal.plantao.transforms import build_cards
from gestaolegal.plantao.views_util import setValoresFormAtendido, tipos_busca_atendidos
from gestaolegal.usuario.models import Endereco, usuario_urole_roles

atendido_controller = Blueprint("atendido", __name__, template_folder="templates")


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


@atendido_controller.route("/atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def atendidos_assistidos():
    page = request.args.get("page", 1, type=int)
    per_page = cast(int, app.config["ATENDIDOS_POR_PAGINA"])

    base_query = (
        db.session.query(Atendido)
        .filter(Atendido.status == True)
        .order_by(Atendido.nome)
    )

    pagination = db.paginate(base_query, page=page, per_page=per_page)

    atendido_ids = [atendido.id for atendido in pagination.items]

    assistidos = {
        a.id_atendido: a
        for a in db.session.query(Assistido)
        .filter(Assistido.id_atendido.in_(atendido_ids))
        .all()
    }

    atendidos_assistidos = []
    for atendido in pagination.items:
        assistido = assistidos.get(atendido.id)
        atendidos_assistidos.append(
            {
                "id": atendido.id,
                "nome": atendido.nome,
                "cpf": atendido.cpf,
                "cnpj": atendido.cnpj,
                "telefone": atendido.telefone,
                "id_atendido": assistido.id_atendido if assistido else None,
                "is_assistido": assistido is not None,
            }
        )

    return render_template(
        "atendidos_assistidos.html",
        atendidos_assistidos=atendidos_assistidos,
        tipos_busca_atendidos=tipos_busca_atendidos,
        pagination=pagination,
        iter_pages=pagination.iter_pages,
    )


@atendido_controller.route("/busca_atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def busca_atendidos_assistidos():
    if request.method == "POST":
        termo = request.form["termo"]
        atendidos = (
            db.session.query(Atendido)
            .join(Assistido)
            .filter(Atendido.nome.like(termo + "%"))
            .all()
        )
        return json.dumps({"atendidos": [x.as_dict() for x in atendidos]})

    return render_template("busca_atendidos_assistidos.html")


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
        return redirect(url_for("atendido.perfil_assistido", _id=_id))

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


@atendido_controller.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id: int):
    result = (
        db.session.query(Atendido, Assistido, AssistidoPessoaJuridica)
        .outerjoin(Assistido, onclause=Assistido.id_atendido == Atendido.id)
        .outerjoin(
            AssistidoPessoaJuridica,
            onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
        )
        .where(Atendido.id == _id)
        .first()
    )

    if not result:
        abort(404)

    atendido = result.tuple()[0]
    assistido = result.tuple()[1]
    assistido_pj = result.tuple()[2]
    cards = build_cards(assistido, atendido, assistido_pj)

    return render_template("perfil_assistidos.html", assistido=result, cards=cards)


@atendido_controller.route("/editar_atendido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def editar_atendido(id_atendido: int):
    atendido = (
        db.session.query(Atendido)
        .where(Atendido.id == id_atendido)
        .where(Atendido.status == True)
        .first()
    )

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
            return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    setValoresFormAtendido(atendido, form)
    return render_template("editar_atendido.html", atendido=atendido, form=form)


@atendido_controller.route("/tornar_assistido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido(id_atendido: int):
    atendido = (
        db.session.query(Atendido)
        .where(Atendido.id == id_atendido)
        .where(Atendido.status == True)
        .first()
    )

    if not atendido:
        abort(404)

    form = TornarAssistidoForm()
    if request.method == "POST":
        if form.validate():
            assistido = Assistido(
                id_atendido=atendido.id,
                sexo=form.sexo.data,
                raca=form.raca.data,
                profissao=form.profissao.data,
                rg=form.rg.data,
                grau_instrucao=form.grau_instrucao.data,
                salario=form.salario.data,
                beneficio=form.qual_beneficio.data,
                contribui_inss=form.contribui_inss.data,
                qtd_pessoas_moradia=form.qtd_pessoas_moradia.data,
                renda_familiar=form.renda_familiar.data,
                participacao_renda=form.participacao_renda.data,
                tipo_moradia=form.tipo_moradia.data,
                possui_outros_imoveis=bool(form.possui_outros_imoveis.data),
                quantos_imoveis=form.quantos_imoveis.data,
                possui_veiculos=bool(form.possui_veiculos.data),
                possui_veiculos_obs=form.possui_veiculos_obs.data,
                quantos_veiculos=form.quantos_veiculos.data,
                ano_veiculo=form.ano_veiculo.data,
                doenca_grave_familia=form.doenca_grave_familia.data,
                pessoa_doente=form.pessoa_doente.data,
                pessoa_doente_obs=form.pessoa_doente_obs.data,
                gastos_medicacao=form.gastos_medicacao.data,
                obs=form.obs_assistido.data,
                # area_direito=form.area_direito.data,
                # observacoes=form.observacoes.data,
            )
            db.session.add(assistido)
            db.session.commit()
            return redirect(url_for("atendido.perfil_assistido", _id=atendido.id))

    return render_template("tornar_assistido.html", atendido=atendido, form=form)
