from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import pytz
from flask import (
    Blueprint,
    flash,
    json,
    redirect,
    render_template,
    request,
    url_for,
    abort,
)
from flask_login import current_user

from gestaolegal import app, db, login_required
from gestaolegal.models.endereco import Endereco
from gestaolegal.notificacoes.models import Notificacao, acoes
from gestaolegal.plantao.forms import (
    AbrirPlantaoForm,
    AssistenciaJudiciariaForm,
    CadastroAtendidoForm,
    CadastroOrientacaoJuridicaForm,
    EditarAssistidoForm,
    FecharPlantaoForm,
    OrientacaoJuridicaForm,
    SelecionarDuracaoPlantaoForm,
    TornarAssistidoForm,
)
from gestaolegal.plantao.models import (
    AssistenciaJudiciaria,
    AssistenciaJudiciaria_xOrientacaoJuridica,
    Assistido,
    AssistidoPessoaJuridica,
    Atendido,
    Atendido_xOrientacaoJuridica,
    DiaPlantao,
    DiasMarcadosPlantao,
    FilaAtendidos,
    OrientacaoJuridica,
    Plantao,
    RegistroEntrada,
    area_atuacao,
    beneficio,
    contribuicao_inss,
    enquadramento,
    escolaridade,
    moradia,
    orgao_reg,
    participacao_renda,
    qual_pessoa_doente,
    regiao_bh,
)
from gestaolegal.plantao.views_util import *
from gestaolegal.usuario.models import (
    Usuario,
    sexo_usuario,
    usuario_urole_inverso,
    usuario_urole_roles,
)
from gestaolegal.utils.models import queryFiltradaStatus


@dataclass
class CardInfo:
    title: str
    body: dict[str, str | None] | str


plantao = Blueprint("plantao", __name__, template_folder="templates")

data_atual = datetime.now().date()


####Cadastrar Atendido
@plantao.route("/novo_atendimento", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_na():
    def valida_dados_form(form: CadastroAtendidoForm):
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

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

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


@plantao.route("/busca_atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def busca_atendidos_assistidos():
    if request.method == "POST":
        termo = request.form["termo"]
        atendidos = db.session.query(Atendido).join(Assistido).filter(
            Atendido.nome.like(termo + "%")
        ).all()
        return json.dumps({"atendidos": [x.as_dict() for x in atendidos]})
    return render_template("busca_atendidos_assistidos.html")


@plantao.route("/atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def listar_atendidos():
    page = request.args.get("page", 1, type=int)
    atendidos = db.session.query(Atendido).join(Assistido).filter(
        Atendido.status == True
    ).paginate(
        page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
    )
    return render_template("atendidos_assistidos.html", atendidos=atendidos)


### Dados do atendido
@plantao.route("/dados_atendido/<int:id>", methods=["GET"])
@login_required()
def dados_atendido(id):
    _atendido = db.session.query(Atendido).filter_by(id=id).first_or_404()
    _form = CadastroAtendidoForm()
    setValoresFormAtendido(_atendido, _form)
    _form.id_atendido = _atendido.id
    return render_template("dados_atendido.html", form=_form)


####Excluir Atendido
@plantao.route("/excluir_atendido/", methods=["POST", "GET"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_atendido():
    id_atendido = request.form.get("id_atendido")
    atendido = db.session.query(Atendido).filter_by(id=id_atendido).first()
    if not atendido:
        abort(404)
    atendido.status = False
    db.session.commit()
    flash("Atendido excluído com sucesso!", "success")
    return redirect(url_for("plantao.listar_atendidos"))


####Editar Atendido
@plantao.route("/editar_atendido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def editar_atendido(id_atendido):
    atendido = db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
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


@plantao.route("/tornar_assistido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido(id_atendido):
    atendido = db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
    if not atendido:
        abort(404)
    form = TornarAssistidoForm()
    if request.method == "POST":
        if form.validate():
            assistido = Assistido(
                atendido_id=atendido.id,
                area_direito=form.area_direito.data,
                observacoes=form.observacoes.data,
                status=True,
            )
            db.session.add(assistido)
            db.session.commit()
            flash("Atendido transformado em assistido com sucesso!", "success")
            return redirect(url_for("plantao.perfil_assistido", _id=atendido.id))
    return render_template("tornar_assistido.html", form=form)


@plantao.route("/editar_assistido/<id_atendido>/", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def editar_assistido(id_atendido):
    assistido = db.session.query(Assistido).filter_by(atendido_id=id_atendido, status=True).first()
    if not assistido:
        abort(404)
    form = TornarAssistidoForm()
    if request.method == "POST":
        if form.validate():
            assistido.area_direito = form.area_direito.data
            assistido.observacoes = form.observacoes.data
            db.session.commit()
            flash("Assistido editado com sucesso!", "success")
            return redirect(url_for("plantao.perfil_assistido", _id=assistido.atendido_id))
    return render_template("editar_assistido.html", form=form)


@plantao.route("/cadastro_orientacao_juridica/", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_orientacao_juridica():
    form = CadastroOrientacaoJuridicaForm()
    if request.method == "POST":
        if form.validate():
            orientacao = OrientacaoJuridica(
                data=form.data.data,
                horario=form.horario.data,
                duracao=form.duracao.data,
                status=True,
            )
            db.session.add(orientacao)
            db.session.commit()
            flash("Orientação jurídica cadastrada com sucesso!", "success")
            return redirect(url_for("plantao.orientacoes_juridicas"))
    return render_template("cadastro_orientacao_juridica.html", form=form)


@plantao.route("/encaminha_assistencia_judiciaria/<int:id_orientacao>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def encaminha_assistencia_judiciaria(id_orientacao):
    orientacao = db.session.query(OrientacaoJuridica).filter_by(id=id_orientacao, status=True).first()
    if not orientacao:
        abort(404)
    form = AssistenciaJudiciariaForm()
    if request.method == "POST":
        if form.validate():
            aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
            aj_oj.id_orientacaoJuridica = orientacao.id
            aj_oj.id_assistenciaJudiciaria = form.areas_atendidas.data
            db.session.add(aj_oj)
            db.session.commit()
            flash("Assistência judiciária cadastrada com sucesso!", "success")
            return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    return render_template("cadastro_assistencia_judiciaria.html", form=form)


@plantao.route(
    "/ajax_multiselect_associa_aj_oj/<int:orientacao_id>", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def ajax_multiselect_associa_aj_oj(orientacao_id):
    orientacao = db.session.query(OrientacaoJuridica).filter_by(id=orientacao_id, status=True).first()
    if not orientacao:
        abort(404)
    
    assistencias = db.session.query(AssistenciaJudiciaria).filter(
        AssistenciaJudiciaria.area_direito == orientacao.area_direito,
        AssistenciaJudiciaria.status == True
    ).all()
    
    return json.dumps({"assistencias": [x.as_dict() for x in assistencias]})


@plantao.route(
    "/associa_orientacao_juridica/<int:id_orientacao>",
    defaults={"id_atendido": 0},
    methods=["POST", "GET"],
)
@plantao.route(
    "/associa_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def associacao_orientacao_juridica(id_orientacao, id_atendido):
    orientacao = db.session.query(OrientacaoJuridica).filter_by(id=id_orientacao, status=True).first()
    if not orientacao:
        abort(404)
    
    if id_atendido:
        atendido = db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
        if not atendido:
            abort(404)
        atendido.orientacoes_juridicas.append(orientacao)
        db.session.commit()
        flash("Atendido associado à orientação jurídica com sucesso!", "success")
    
    return redirect(url_for("plantao.perfil_oj", id=id_orientacao))


@plantao.route(
    "/desassociar_orientacao_juridica/<int:id_orientacao>/<int:id_atendido>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def desassociar_orientacao_juridica(id_atendido, id_orientacao):
    orientacao = db.session.query(OrientacaoJuridica).filter_by(id=id_orientacao, status=True).first()
    if not orientacao:
        abort(404)
    
    atendido = db.session.query(Atendido).filter_by(id=id_atendido, status=True).first()
    if not atendido:
        abort(404)
    
    atendido.orientacoes_juridicas.remove(orientacao)
    db.session.commit()
    flash("Atendido desassociado da orientação jurídica com sucesso!", "success")
    return redirect(url_for("plantao.perfil_oj", id=id_orientacao))


# Busca dos atendidos para associar a uma orientação jurídica
@plantao.route("/busca_atendidos_oj/", defaults={"_busca": None})
@plantao.route("/busca_atendidos_oj/<_busca>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def busca_atendidos_oj(_busca):
    page = request.args.get("page", 1, type=int)
    query = db.session.query(Atendido).filter(Atendido.status == True)
    
    if _busca:
        query = query.filter(
            (Atendido.nome.ilike(f"%{_busca}%")) |
            (Atendido.cpf.ilike(f"%{_busca}%")) |
            (Atendido.cnpj.ilike(f"%{_busca}%"))
        )
    
    atendidos = query.order_by(Atendido.nome).paginate(
        page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
    )
    
    return render_template("busca_atendidos_oj.html", atendidos=atendidos, busca=_busca)


@plantao.route("/excluir_orientacao_juridica/", methods=["POST"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_oj():
    id_orientacao = request.form.get("id_orientacao")
    orientacao = db.session.query(OrientacaoJuridica).filter_by(id=id_orientacao, status=True).first()
    if not orientacao:
        abort(404)
    orientacao.status = False
    db.session.commit()
    flash("Orientação jurídica excluída com sucesso!", "success")
    return redirect(url_for("plantao.orientacoes_juridicas"))


@plantao.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id):
    assistido = db.session.query(Assistido).filter_by(atendido_id=_id, status=True).first()
    if not assistido:
        abort(404)
    
    orientacoes = db.session.query(OrientacaoJuridica).join(
        Assistido.orientacoes_juridicas
    ).filter(
        Assistido.id == assistido.id,
        OrientacaoJuridica.status == True
    ).all()
    
    return render_template(
        "perfil_assistido.html",
        assistido=assistido,
        orientacoes=orientacoes
    )


@plantao.route("/editar_orientacao_juridica/<id_oj>", methods=["POST", "GET"])
@login_required(
    role=[usuario_urole_roles["ADMINISTRADOR"][0], usuario_urole_roles["PROFESSOR"][0]]
)
def editar_orientacao_juridica(id_oj):
    def setDadosOrientacaoJuridica(
        entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm
    ):
        entidade_orientacao.area_direito = form.area_direito.data
        entidade_orientacao.descricao = form.descricao.data
        entidade_orientacao.setSubAreas(
            entidade_orientacao.area_direito,
            form.sub_area.data,
            form.sub_areaAdmin.data,
        )

    def setOrientacaoJuridicaForm(
        entidade_orientacao: OrientacaoJuridica, form: OrientacaoJuridicaForm
    ):
        form.area_direito.data = entidade_orientacao.area_direito
        form.sub_area.data = entidade_orientacao.sub_area
        form.descricao.data = entidade_orientacao.descricao

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_orientacao = db.session.query(OrientacaoJuridica).filter_by(
        id=id_oj, status=True
    ).first()

    if not entidade_orientacao:
        flash("Essa orientação não existe!", "warning")
        return redirect(url_for("plantao.orientacoes_juridicas"))

    form = OrientacaoJuridicaForm()
    if request.method == "POST":
        if not form.validate():
            return render_template("editar_orientacao_juridica.html", form=form)

        setDadosOrientacaoJuridica(entidade_orientacao, form)
        db.session.commit()
        flash("Orientação Jurídica editada com sucesso!", "success")
        return redirect(url_for("plantao.orientacoes_juridicas"))

    setOrientacaoJuridicaForm(entidade_orientacao, form)
    return render_template(
        "editar_orientacao_juridica.html", form=form, orientacao=entidade_orientacao
    )


# Busca da página de orientações jurídicas
@plantao.route("/busca_oj/", defaults={"_busca": None})
@plantao.route("/busca_oj/<_busca>", methods=["GET"])
@login_required()
def busca_oj(_busca):
    page = request.args.get("page", 1, type=int)
    if _busca is None:
        orientacoes = (
            queryFiltradaStatus(OrientacaoJuridica)
            .order_by(OrientacaoJuridica.id.desc())
            .paginate(
                page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
            )
        )
    else:
        orientacoes = (
            queryFiltradaStatus(OrientacaoJuridica)
            .outerjoin(
                Atendido_xOrientacaoJuridica,
                OrientacaoJuridica.id
                == Atendido_xOrientacaoJuridica.id_orientacaoJuridica,
            )
            .outerjoin(
                Atendido, Atendido.id == Atendido_xOrientacaoJuridica.id_atendido
            )
            .filter(
                ((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca)))
            )
            .order_by(OrientacaoJuridica.id.desc())
            .paginate(
                page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
            )
        )

    return render_template("busca_orientacoes_juridicas.html", orientacoes=orientacoes)


# Excluir assistência judiciária
@plantao.route("/excluir_assistencia_judiciaria/<int:id>", methods=["POST"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_assistencia_judiciaria(id):
    assistencia = db.session.query(AssistenciaJudiciaria).filter_by(
        id=id,
        status=True
    ).first()
    
    if not assistencia:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    
    assistencia.status = False
    db.session.commit()
    flash("Assistência judiciária excluída com sucesso!", "success")
    return redirect(url_for("plantao.listar_assistencias_judiciarias"))


# Busca da página de assistências judiciárias
@plantao.route("/busca_assistencia_judiciaria/", methods=["GET", "POST"])
@login_required()
def busca_assistencia_judiciaria():
    page = request.args.get("page", 1, type=int)
    _busca = request.args.get("busca", "", type=str)
    filtro = request.args.get(
        "opcao_filtro", filtro_busca_assistencia_judiciaria["TODAS"][0], type=str
    )

    assistencias = query_busca_assistencia_judiciaria(
        db.session.query(AssistenciaJudiciaria), _busca
    )
    assistencias = query_filtro_assistencia_judiciaria(assistencias, filtro).paginate(
        page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
    )

    return render_template(
        "busca_assistencia_judiciaria.html", assistencias=assistencias
    )


# Perfil da assistência judiciária
@plantao.route("/perfil_assistencia_judiciaria/<_id>")
@login_required()
def perfil_assistencia_judiciaria(_id):
    aj = (
        db.session.query(AssistenciaJudiciaria, Endereco)
        .select_from(AssistenciaJudiciaria)
        .join(Endereco)
        .filter((AssistenciaJudiciaria.id == _id))
        .first()
    )
    if aj is None:
        flash("Assistência judiciária não encontrada.", "warning")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    return render_template("visualizar_assistencia_judiciaria.html", aj=aj)


# Página de plantao
@plantao.route("/pagina_plantao", methods=["POST", "GET"])
@login_required()
def pg_plantao():
    dias_usuario_marcado = db.session.query(DiasMarcadosPlantao).filter_by(
        id_usuario=current_user.id,
        status=True,
    ).all()

    plantao = db.session.query(Plantao).first()

    apaga_dias_marcados(plantao, dias_usuario_marcado)
    try:
        if (
            current_user.urole
            not in [
                usuario_urole_roles["ADMINISTRADOR"][0],
                usuario_urole_roles["COLAB_PROJETO"][0],
            ]
        ) and (plantao.data_abertura == None):
            flash("O plantão não está aberto!")
            return redirect(url_for("principal.index"))

        dias_usuario_atual = db.session.query(DiasMarcadosPlantao).filter_by(
            id_usuario=current_user.id,
            status=True,
        ).all()

        return render_template(
            "pagina_plantao.html",
            datas_plantao=dias_usuario_atual,
            numero_plantao=numero_plantao_a_marcar(current_user.id),
            data_atual=data_atual,
        )
    except AttributeError:
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))


@plantao.route("/ajax_obter_escala_plantao", methods=["GET"])
@login_required()
def ajax_obter_escala_plantao():
    escala = []

    datas_ja_marcadas = db.session.query(DiasMarcadosPlantao).filter(
        DiasMarcadosPlantao.status == True
    ).all()
    for registro in datas_ja_marcadas:
        if registro.usuario.status:
            escala.append(
                {
                    "nome": registro.usuario.nome,
                    "day": registro.data_marcada.day,
                    "month": registro.data_marcada.month,
                    "year": registro.data_marcada.year,
                }
            )
    return app.response_class(
        response=json.dumps(escala), status=200, mimetype="application/json"
    )


@plantao.route("/ajax_obter_duracao_plantao", methods=["GET", "POST"])
@login_required()
def ajax_obter_duracao_plantao():
    dias_duracao = []

    dias_duracao_gravados = db.session.query(DiaPlantao).filter(DiaPlantao.status == True).all()
    for dia_duracao in dias_duracao_gravados:
        dias_duracao.append(dia_duracao.data)

    return app.response_class(
        response=json.dumps(dias_duracao), status=200, mimetype="application/json"
    )


@plantao.route("/ajax_confirma_data_plantao", methods=["POST", "GET"])
@login_required()
def ajax_confirma_data_plantao():
    def cria_json(lista_datas, mensagem, tipo_mensagem: str):
        return {
            "lista_datas": lista_datas,
            "mensagem": mensagem,
            "tipo_mensagem": tipo_mensagem,
            "numero_plantao": numero_plantao_a_marcar(current_user.id),
        }

    plantao = db.session.query(Plantao).first()
    valida_fim_plantao(plantao)
    if (
        current_user.urole
        not in [
            usuario_urole_roles["ADMINISTRADOR"][0],
            usuario_urole_roles["COLAB_PROJETO"][0],
        ]
    ) and (plantao.data_abertura == None):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    dias_abertos_plantao = db.session.query(DiaPlantao).filter_by(status=1).all()
    lista_dias_abertos = []
    for dia_aberto in dias_abertos_plantao:
        lista_dias_abertos.append(dia_aberto.data)

    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")
    data_marcada = date(int(ano), int(mes), int(dia))
    tipo_mensagem = ""
    mensagem = ""
    resultado_json = {}

    dias_usuario_marcado = db.session.query(DiasMarcadosPlantao).filter_by(
        id_usuario=current_user.id, status=True
    ).all()

    validacao = data_marcada in lista_dias_abertos
    if not validacao:
        tipo_mensagem = "warning"
        mensagem = "Data selecionada não foi aberta para plantão."
        resultado_json = cria_json(
            render_template(
                "lista_datas_plantao.html",
                data_atual=data_atual,
                datas_plantao=dias_usuario_marcado,
            ),
            mensagem,
            tipo_mensagem,
        )
        return app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if not confirma_disponibilidade_dia(lista_dias_abertos, data_marcada):
        tipo_mensagem = "warning"
        mensagem = "Não há vagas disponíveis na data selecionada, tente outro dia."
        resultado_json = cria_json(
            render_template(
                "lista_datas_plantao.html",
                datas_plantao=dias_usuario_marcado,
                data_atual=data_atual,
            ),
            mensagem,
            tipo_mensagem,
        )
        return app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if len(dias_usuario_marcado) >= 2 or (
        len(dias_usuario_marcado) >= 1
        and current_user.urole == usuario_urole_roles["ORIENTADOR"][0]
    ):
        tipo_mensagem = "warning"
        mensagem = "Você atingiu o limite de plantões cadastrados."
        resultado_json = cria_json(
            render_template(
                "lista_datas_plantao.html",
                datas_plantao=dias_usuario_marcado,
                data_atual=data_atual,
            ),
            mensagem,
            tipo_mensagem,
        )
        return app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if data_marcada in [dia.data_marcada for dia in dias_usuario_marcado]:
        tipo_mensagem = "warning"
        mensagem = "Você já marcou plantão neste dia!"
        resultado_json = cria_json(
            render_template(
                "lista_datas_plantao.html",
                datas_plantao=dias_usuario_marcado,
                data_atual=data_atual,
            ),
            mensagem,
            tipo_mensagem,
        )
        return app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    dia_marcado = DiasMarcadosPlantao(
        data_marcada=data_marcada, id_usuario=current_user.id, status=True
    )
    db.session.add(dia_marcado)
    db.session.commit()
    mensagem = "Data de plantão cadastrada!"
    tipo_mensagem = "success"
    dias_usuario_atual = db.session.query(DiasMarcadosPlantao).filter_by(
        id_usuario=current_user.id, status=True
    ).all()
    resultado_json = cria_json(
        render_template(
            "lista_datas_plantao.html",
            datas_plantao=dias_usuario_atual,
            data_atual=data_atual,
        ),
        mensagem,
        tipo_mensagem,
    )
    return app.response_class(
        response=json.dumps(resultado_json), status=200, mimetype="application/json"
    )


@plantao.route("/editar_plantao", methods=["GET"])
@login_required()
def editar_plantao():
    dias_marcados_plantao = db.session.query(DiasMarcadosPlantao).filter_by(
        id_usuario=current_user.id, status=True
    ).all()
    for dia in dias_marcados_plantao:
        dia.status = False

    db.session.commit()
    flash(
        "Registro apagado. Por favor, selecione novamente os dias para o seu plantão",
        "Success",
    )
    return redirect(url_for("plantao.pg_plantao"))


@plantao.route("/ajax_disponibilidade_de_vagas", methods=["POST", "GET"])
@login_required()
def ajax_disponibilidade_de_vagas():
    ano = request.args.get("ano")
    mes = request.args.get("mes")

    dias = []

    dias_abertos_plantao = db.session.query(DiaPlantao).filter_by(status=1).all()
    lista_dias_abertos = []

    for dia_aberto in dias_abertos_plantao:
        if dia_aberto.data.month == int(mes) and dia_aberto.data.year == int(ano):
            lista_dias_abertos.append(dia_aberto.data)

    for data in lista_dias_abertos:
        if confirma_disponibilidade_dia(lista_dias_abertos, data):
            index = {"Dia": str(data.day), "Vagas": True}
            dias.append(index)
        else:
            index = {"Dia": str(data.day), "Vagas": False}
            dias.append(index)

    response = app.response_class(
        response=json.dumps(dias), status=200, mimetype="application/json"
    )
    return response


@plantao.route("/ajax_vagas_disponiveis", methods=["POST", "GET"])
@login_required()
def ajax_vagas_disponiveis():
    ano = request.args.get("ano")
    mes = request.args.get("mes")
    dia = request.args.get("dia")

    dias_abertos_plantao = db.session.query(DiaPlantao).filter_by(status=1).all()
    lista_dias_abertos = []

    for dia_aberto in dias_abertos_plantao:
        lista_dias_abertos.append(dia_aberto.data)

    data_marcada = date(int(ano), int(mes), int(dia))
    num_vagas = vagas_restantes(lista_dias_abertos, data_marcada)
    index = {"NumeroVagas": num_vagas}

    response = app.response_class(
        response=json.dumps(index), status=200, mimetype="application/json"
    )
    return response


# Registro de presença do plantao
@plantao.route("/registro_presenca")
@login_required()
def reg_presenca():
    data_hora_atual = datetime.now(tz=pytz.timezone("America/Sao_Paulo"))
    status_presenca = "Entrada"

    verifica_historico = db.session.query(RegistroEntrada).filter(
        RegistroEntrada.id_usuario == current_user.id, RegistroEntrada.status == True
    ).first()
    if verifica_historico:
        if (
            (data_hora_atual.day - verifica_historico.data_saida.day >= 1)
            or (data_hora_atual.month - verifica_historico.data_saida.month >= 1)
            or (data_hora_atual.year - verifica_historico.data_saida.year >= 1)
        ):
            verifica_historico.status = False
            db.session.commit()
        else:
            status_presenca = "Saída"

    return render_template(
        "registro_presenca.html",
        data_hora_atual=data_hora_atual,
        status_presenca=status_presenca,
    )


@plantao.route("/ajax_registra_presenca", methods=["POST"])
@login_required()
def ajax_registra_presenca():
    def cria_json(mensagem: str, tipo_mensagem: str, status: str) -> dict:
        return {"mensagem": mensagem, "tipo_mensagem": tipo_mensagem, "status": status}

    data_atual = date.today()
    hora_registrada = request.json["hora_registrada"].split(":")
    hora_formatada = time(int(hora_registrada[0]), int(hora_registrada[1]))
    data_hora_registrada = datetime.combine(data_atual, hora_formatada)

    verifica_historico = db.session.query(RegistroEntrada).filter(
        RegistroEntrada.id_usuario == current_user.id, RegistroEntrada.status == True
    ).first()
    if verifica_historico:
        verifica_historico.data_saida = data_hora_registrada
        verifica_historico.status = False

        db.session.commit()

        resposta = cria_json(
            "Hora de saída registrada com sucesso!", "success", "Entrada"
        )

        return app.response_class(
            response=json.dumps(resposta), status=200, mimetype="application/json"
        )

    novo_registro = RegistroEntrada(
        data_entrada=data_hora_registrada,
        data_saida=datetime.combine(date.today(), time(23, 59, 59)),
        id_usuario=current_user.id,
    )

    db.session.add(novo_registro)
    db.session.commit()

    resposta = cria_json("Hora de entrada registrada com sucesso", "success", "Saída")

    return app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


@plantao.route("/confirmar_presenca", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def confirmar_presenca():
    if request.method == "POST":
        dados_cru = request.form.to_dict()
        dados = [(chave, dados_cru[chave]) for chave in dados_cru.keys()]

        for i in range(1, len(dados)):
            tipo_confirmacao = dados[i][0].split("_")

            if tipo_confirmacao[0] == "plantao":
                plantao = db.session.query(DiasMarcadosPlantao).get_or_404(int(tipo_confirmacao[1]))
                plantao.confirmacao = dados[i][1]

                db.session.commit()

            else:
                presenca = db.session.query(RegistroEntrada).get_or_404(int(tipo_confirmacao[1]))
                presenca.confirmacao = dados[i][1]

                db.session.commit()

    if (
        date.today().weekday() != 1
    ):  # Se for um dia diferente de segunda, lista as presencas de ontem
        data_ontem = date.today() - timedelta(days=1)

        presencas_registradas = db.session.query(RegistroEntrada).filter(
            RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
        ).all()
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = db.session.query(DiasMarcadosPlantao).filter(
            DiasMarcadosPlantao.data_marcada == data_ontem,
            DiasMarcadosPlantao.confirmacao == "aberto",
        ).all()

    else:
        data_ontem = date.today() - timedelta(
            days=3
        )  # Se for segunda, lista as presenças

        presencas_registradas = db.session.query(RegistroEntrada).filter(
            RegistroEntrada.status == False
        ).all()
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = db.session.query(DiasMarcadosPlantao).filter(
            DiasMarcadosPlantao.data_marcada == data_ontem,
            DiasMarcadosPlantao.confirmacao == "aberto",
        ).all()

    return render_template(
        "confirmar_presenca.html",
        presencas_registradas=presencas_ontem,
        plantoes_registradas=plantoes_ontem,
        usuario_urole_inverso=usuario_urole_inverso,
        data_ontem=data_ontem,
    )


@plantao.route("/ajax_busca_presencas_data", methods=["POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def ajax_busca_presencas_data():
    def cria_json(
        presencas: list, plantoes: list, tem_presenca: bool, tem_plantao: bool
    ) -> dict:
        return {
            "presencas": presencas,
            "plantoes": plantoes,
            "tem_presenca": tem_presenca,
            "tem_plantao": tem_plantao,
        }

    data_procurada_string = request.json["nova_data"]
    data_procurada_separada = data_procurada_string.split("-")
    data_procurada = date(
        int(data_procurada_separada[0]),
        int(data_procurada_separada[1]),
        int(data_procurada_separada[2]),
    )

    presencas_registradas = db.session.query(RegistroEntrada).filter(
        RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
    ).all()
    presencas = [
        presenca
        for presenca in presencas_registradas
        if presenca.data_entrada.date() == data_procurada
    ]

    plantoes_marcados = db.session.query(DiasMarcadosPlantao).filter(
        DiasMarcadosPlantao.data_marcada == data_procurada,
        DiasMarcadosPlantao.confirmacao == "aberto",
    ).all()

    presencas_ajax = [
        {
            "IdPresenca": presenca.id,
            "Nome": presenca.usuario.nome,
            "Cargo": usuario_urole_inverso[presenca.usuario.urole],
            "Entrada": presenca.data_entrada.strftime("%H:%M"),
            "Saida": presenca.data_saida.strftime("%H:%M"),
        }
        for presenca in presencas
    ]
    plantoes_ajax = [
        {
            "IdPlantao": plantao.id,
            "Nome": plantao.usuario.nome,
            "Cargo": usuario_urole_inverso[plantao.usuario.urole],
        }
        for plantao in plantoes_marcados
    ]

    tem_presenca = False
    tem_plantao = False

    if presencas:
        tem_presenca = True
    if plantoes_marcados:
        tem_plantao = True

    resposta = cria_json(presencas_ajax, plantoes_ajax, tem_presenca, tem_plantao)

    return app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


@plantao.route("/configurar_abertura", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
    ]
)
def configurar_abertura():
    form_abrir = AbrirPlantaoForm()
    form_fechar = FecharPlantaoForm()
    hoje = datetime.now()
    _form = SelecionarDuracaoPlantaoForm()

    dias_plantao = (
        db.session.query(DiaPlantao.data).filter(DiaPlantao.status == True).all()
    )
    # dias_sem_plantao = db.session.query(DiaSemPlantao.data).filter(DiaSemPlantao.ano == str(date.today().year)).all()

    dias_front = [
        (data.data.year, data.data.month, data.data.day) for data in dias_plantao
    ]

    plantao = db.session.query(Plantao).first()

    valida_fim_plantao(plantao)
    if (
        current_user.urole
        not in [
            usuario_urole_roles["ADMINISTRADOR"][0],
            usuario_urole_roles["COLAB_PROJETO"][0],
        ]
    ) and (plantao.data_abertura == None):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    set_abrir_plantao_form(form_abrir, plantao)
    set_fechar_plantao_form(form_fechar, plantao)

    _notificacao = Notificacao(
        acao=acoes["ABERTURA_PLANTAO"].format(),
        data=datetime.now(),
        id_executor_acao=current_user.id,
        id_usu_notificar=current_user.id,
    )
    db.session.add(_notificacao)
    db.session.commit()

    return render_template(
        "configurar_abertura.html",
        form_fechar=form_fechar,
        form_abrir=form_abrir,
        periodo=f"{hoje.month + 1:02}/{hoje.year}",
        form=_form,
        dias_front=dias_front,
    )


@plantao.route("/ajax_salva_config_plantao", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
    ]
)
def ajax_salva_config_plantao():
    def cria_json(mensagem: str, tipo_mensagem: str) -> dict:
        return {
            "mensagem": mensagem,
            "tipo_mensagem": tipo_mensagem,
        }

    datas_duracao = request.json["datas_duracao"]
    data_abertura = request.json["data_abertura"]
    hora_abertura = request.json["hora_abertura"]
    data_fechamento = request.json["data_fechamento"]
    hora_fechamento = request.json["hora_fechamento"]
    plantao = db.session.query(Plantao).first()

    status_data_abertura = False
    status_data_fechamento = False

    lista_duracao_banco_dados = db.session.query(DiaPlantao.data, DiaPlantao.id).all()

    if datas_duracao:
        # converte as strings, retornadas pelo front, em objetos do tipo date.

        for i in range(len(datas_duracao)):
            datas_duracao[i] = datetime.strptime(
                datas_duracao[i][0:10], "%d/%m/%Y"
            ).date()

        # Se dia no front não esta no banco, adicionar no banco.
        datas_duracao_banco_dados = [data[0] for data in lista_duracao_banco_dados]
        for data in datas_duracao:
            if data not in datas_duracao_banco_dados:
                nova_data = DiaPlantao(data=data)
                db.session.add(nova_data)
                db.session.flush()

        # Se dia do banco não estava no front, apagar no banco.
        for duracao in lista_duracao_banco_dados:
            if duracao[0] not in datas_duracao:
                db.session.query(DiaPlantao).filter(DiaPlantao.id == duracao[1]).delete()
                db.session.flush()
                print("Se dia do banco não estava no front, apagar no banco.")

        db.session.commit()

    if data_abertura and hora_abertura:
        data_abertura_escolhida = data_abertura.split("-")
        hora_abertura_escolhida = hora_abertura.split(":")
        data_abertura_formatada = date(
            int(data_abertura_escolhida[0]),
            int(data_abertura_escolhida[1]),
            int(data_abertura_escolhida[2]),
        )
        hora_abertura_formatada = time(
            int(hora_abertura_escolhida[0]), int(hora_abertura_escolhida[1]), 0
        )
        data_abertura_nova = datetime.combine(
            data_abertura_formatada, hora_abertura_formatada
        )

        if not plantao:
            plantao = Plantao(data_abertura=data_abertura_nova)

            db.session.add(plantao)
            db.session.commit()
            app.config["ID_PLANTAO"] = plantao.id

            status_data_abertura = True

        else:
            plantao.data_abertura = data_abertura_nova

            db.session.commit()

            status_data_abertura = True

        _notificacao = Notificacao(
            acao=acoes["ABERTURA_PLANTAO"],
            data=datetime.now(),
            id_executor_acao=current_user.id,
        )
        db.session.add(_notificacao)
        db.session.commit()

    if data_fechamento and hora_fechamento:
        data_fechamento_escolhida = data_fechamento.split("-")
        hora_fechamento_escolhida = hora_fechamento.split(":")
        data_fechamento_formatada = date(
            int(data_fechamento_escolhida[0]),
            int(data_fechamento_escolhida[1]),
            int(data_fechamento_escolhida[2]),
        )
        hora_fechamento_formatada = time(
            int(hora_fechamento_escolhida[0]), int(hora_fechamento_escolhida[1]), 0
        )
        data_fechamento_nova = datetime.combine(
            data_fechamento_formatada, hora_fechamento_formatada
        )

        if not plantao:
            plantao = Plantao(data_fechamento=data_fechamento_nova)

            db.session.add(plantao)
            db.session.commit()
            app.config["ID_PLANTAO"] = plantao.id

            status_data_fechamento = True

        else:
            plantao.data_fechamento = data_fechamento_nova

            db.session.commit()

            status_data_fechamento = True

    resposta = {}

    if status_data_abertura and status_data_fechamento:
        resposta = cria_json(
            "Data de abertura e fechamento do plantão configurada com sucesso!",
            "success",
        )

    elif status_data_abertura and not status_data_fechamento:
        resposta = cria_json("Data de fechamento não pôde ser configurada!", "warning")

    elif not status_data_abertura and status_data_fechamento:
        resposta = cria_json("Data de abertura não pôde ser configurada!", "warning")

    else:
        resposta = cria_json(
            "Não foi possível configurar as datas de abertura e fechamento!", "warning"
        )

    return app.response_class(
        response=json.dumps(resposta), status=200, mimetype="application/json"
    )


# ENDPOINTS DE MELHORIA
### Retorna lista de atendidos
@plantao.route("/todos-atendidos", methods=["GET", "POST"])
@login_required()
def pega_atendidos():
    atendidos = busca_atendidos_modal()
    return json.dumps(atendidos)


### Retorna lista de assistencia judiciaria
@plantao.route("/todas-assistencias-judiciarias", methods=["GET", "POST"])
@login_required()
def pega_assistencias_judiciarias():
    assistencias_judiciarias = busca_assistencias_judiciarias_modal()
    return json.dumps(assistencias_judiciarias)


@plantao.route("/tornar_assistido_modal/", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido_modal():
    if request.method == "GET":
        return json.dumps({"hello": "world"})
    data = request.get_json(silent=True, force=True)
    if data["action"] == "modal":
        entidade_assistido = Assistido()
        entidade_assistido.id_atendido = data["id_atendido"]
        entidade_assistido.sexo = data["sexo"]
        entidade_assistido.raca = data["raca"]
        entidade_assistido.profissao = data["profissao"]
        entidade_assistido.rg = data["rg"]
        entidade_assistido.grau_instrucao = data["grau_instrucao"]
        entidade_assistido.salario = data["salario"]
        entidade_assistido.beneficio = data["beneficio"]
        entidade_assistido.qual_beneficio = data["qual_beneficio"]
        entidade_assistido.contribui_inss = data["contribui_inss"]
        entidade_assistido.qtd_pessoas_moradia = data["qtd_pessoas_moradia"]
        entidade_assistido.renda_familiar = data["renda_familiar"]
        entidade_assistido.participacao_renda = data["participacao_renda"]
        entidade_assistido.tipo_moradia = data["tipo_moradia"]
        entidade_assistido.possui_outros_imoveis = (
            True if data["possui_outros_imoveis"] == "Não" else False
        )
        entidade_assistido.quantos_imoveis = (
            0 if data["quantos_imoveis"] == "" else data["quantos_imoveis"]
        )
        entidade_assistido.possui_veiculos = (
            True if data["possui_veiculos"] == "Não" else False
        )
        entidade_assistido.doenca_grave_familia = data["doenca_grave_familia"]
        entidade_assistido.obs = data["obs_assistido"]

        entidade_assistido.setCamposVeiculo(
            entidade_assistido.possui_veiculos,
            data["possui_veiculos_obs"],
            0 if data["quantos_veiculos"] == "" else data["quantos_veiculos"],
            data["ano_veiculo"],
        )
        entidade_assistido.setCamposDoenca(
            entidade_assistido.doenca_grave_familia,
            data["pessoa_doente"],
            data["pessoa_doente_obs"],
            0 if data["gastos_medicacao"] == "" else data["gastos_medicacao"],
        )
        db.session.add(entidade_assistido)
        db.session.commit()

        return json.dumps(
            {
                "status": "success",
                "message": "Assistido cadastrado com sucesso!",
                "id": data["id_atendido"],
            }
        )
    else:
        return json.dumps(
            {"status": "error", "message": "Campo de ação não encontrado"}
        )


@plantao.route("/verifica_assistido/<_id>", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def verifica_assistdo(_id):
    if request.method == "POST":
        return json.dumps({"hello": "world"})
    verificado = db.session.query(Assistido).filter(Assistido.id_atendido == _id).first()
    return json.dumps({"assistido": True if verificado else False})


@plantao.route("/fila-atendimento", methods=["GET", "POST"])
@login_required()
def fila_atendimento():
    return render_template("lista_atendimentos.html")


@plantao.route("/fila-atendimento/criar", methods=["GET", "POST"])
@login_required()
def criar_fila():
    if request.method == "GET":
        return json.dumps({"error": "error to access the page"})
    data = request.get_json(silent=True, force=True)

    psicologia = data["psicologia"]
    prioridade = data["prioridade"]
    senha = data["senha"]
    id_atendido = data["id_atendido"]
    fila = FilaAtendidos()
    fila.psicologia = psicologia
    fila.prioridade = prioridade
    fila.data_criacao = datetime.now()
    fila.senha = senha
    fila.id_atendido = id_atendido
    fila.status = 0
    db.session.add(fila)
    db.session.commit()
    return json.dumps({"message": "success" if fila.id else "error"})


@plantao.route("/fila-atendimento/gerar-senha/<prioridade>", methods=["GET"])
@login_required()
def gerar_senha(prioridade):
    today = datetime.now()
    senha = (
        len(
            db.session.query(FilaAtendidos).filter(
                FilaAtendidos.prioridade == prioridade,
                FilaAtendidos.data_criacao.between(
                    today.strftime("%Y-%m-%d 00:00:00"),
                    today.strftime("%Y-%m-%d 23:59:59"),
                ),
            ).all()
        )
        + 1
    )
    senha = "0" + str(senha) if senha < 10 else str(senha)
    return json.dumps({"senha": senha})


@plantao.route("/fila-atendimento/hoje", methods=["GET", "PUT"])
@login_required()
def pegar_atendimentos():
    if request.method == "PUT":
        data = request.get_json(silent=True, force=True)
        id = data["id"]
        fila = db.session.query(FilaAtendidos).filter(FilaAtendidos.id == id).first()
        fila.status = data["status"]
        try:
            db.session.commit()
            return json.dumps({"message": "Status atualizado com sucesso"})
        except:
            return json.dumps({"message": "Ocorreu um erro durante a atualização"})

    today = datetime.now()
    fila = db.session.query(FilaAtendidos).filter(
        FilaAtendidos.data_criacao.between(
            today.strftime("%Y-%m-%d 00:00:00"), today.strftime("%Y-%m-%d 23:59:59")
        )
    ).all()
    fila_obj = []
    for f in fila:
        fila_obj.append(
            {
                "id": f.id,
                "nome": f.atendido.nome,
                "senha": f.senha,
                "hora": f.data_criacao,
                "prioridade": f.prioridade,
                "psicologia": "Sim" if f.psicologia else "Não",
                "status": f.status,
            }
        )
    return json.dumps(fila_obj)


@plantao.route("/atendido/fila-atendimento", methods=["GET", "POST"])
@login_required()
def ajax_cadastrar_atendido():
    data = request.get_json(silent=True, force=True)
    # form = CadastroAtendidoForm()
    entidade_endereco = Endereco(
        logradouro=data["logradouro"],
        numero=data["numero"],
        complemento=data["complemento"],
        bairro=data["bairro"],
        cep=data["cep"],
        cidade=data["cidade"],
        estado=data["estado"],
    )
    db.session.add(entidade_endereco)
    db.session.flush()
    entidade_atendido = Atendido(
        nome=data["nome"],
        data_nascimento=data["data_nascimento"],
        cpf=data["cpf"],
        cnpj=data["cnpj"],
        telefone=data["telefone"],
        celular=data["celular"],
        email=data["email"],
        estado_civil=data["estado_civil"],
        como_conheceu=data["como_conheceu"],
        indicacao_orgao=data["indicacao_orgao"],
        procurou_outro_local=data["procurou_outro_local"],
        procurou_qual_local=data["procurou_qual_local"],
        obs=data["obs_atendido"],
        endereco_id=entidade_endereco.id,
        pj_constituida=1 if data["pj_constituida"] == "True" else 0,
        repres_legal=1 if data["repres_legal"] == "True" else 0,
        nome_repres_legal=data["nome_repres_legal"],
        cpf_repres_legal=data["cpf_repres_legal"],
        contato_repres_legal=data["contato_repres_legal"],
        rg_repres_legal=data["rg_repres_legal"],
        nascimento_repres_legal=data["nascimento_repres_legal"],
        pretende_constituir_pj=data["pretende_constituir_pj"],
        status=1,
    )
    entidade_atendido.setIndicacao_orgao(
        data["indicacao_orgao"], entidade_atendido.como_conheceu
    )
    entidade_atendido.setCnpj(
        entidade_atendido.pj_constituida, data["cnpj"], 1 if data["repres_legal"] else 0
    )

    entidade_atendido.setRepres_legal(
        entidade_atendido.repres_legal,
        entidade_atendido.pj_constituida,
        data["nome_repres_legal"],
        data["cpf_repres_legal"],
        data["contato_repres_legal"],
        data["rg_repres_legal"],
        data["nascimento_repres_legal"],
    )

    entidade_atendido.setProcurou_qual_local(
        entidade_atendido.procurou_outro_local, data["procurou_qual_local"]
    )
    db.session.add(entidade_atendido)
    db.session.commit()
    return json.dumps({"id": entidade_atendido.id, "nome": entidade_atendido.nome})


@plantao.route("/orientacoes_juridicas")
@login_required()
def orientacoes_juridicas():
    page = request.args.get("page", 1, type=int)
    orientacoes = db.session.query(OrientacaoJuridica).filter_by(
        status=True
    ).order_by(
        OrientacaoJuridica.id.desc()
    ).paginate(
        page=page, 
        per_page=app.config["ATENDIDOS_POR_PAGINA"], 
        error_out=False
    )
    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


@plantao.route("/orientacao_juridica/<id>")
@login_required()
def perfil_oj(id):
    orientacao = db.session.query(OrientacaoJuridica).get_or_404(id)
    
    atendidos_envolvidos = db.session.query(Atendido).join(
        Atendido_xOrientacaoJuridica
    ).filter(
        Atendido_xOrientacaoJuridica.id_orientacaoJuridica == orientacao.id,
        Atendido.status == True
    ).order_by(Atendido.nome).all()
    
    usuario = None
    if orientacao.id_usuario:
        usuario = db.session.query(Usuario).filter_by(id=orientacao.id_usuario).first()
    
    assistencias_envolvidas = db.session.query(AssistenciaJudiciaria_xOrientacaoJuridica).filter_by(
        id_orientacaoJuridica=orientacao.id
    ).all()
    
    return render_template(
        "perfil_orientacao_juridica.html",
        orientacao=orientacao,
        atendidos=atendidos_envolvidos,
        assistencias=assistencias_envolvidas,
        usuario=usuario or {"nome": "--"}
    )


@plantao.route("/assistencias_judiciarias/", methods=["POST", "GET"])
@login_required()
def listar_assistencias_judiciarias():
    page = request.args.get("page", 1, type=int)
    assistencias = db.session.query(AssistenciaJudiciaria).filter_by(
        status=True
    ).order_by(
        AssistenciaJudiciaria.nome
    ).paginate(
        page=page,
        per_page=app.config["ATENDIDOS_POR_PAGINA"],
        error_out=False
    )
    return render_template(
        "lista_assistencia_judiciaria.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria
    )


@plantao.route("/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def editar_assistencia_judiciaria(id_assistencia_judiciaria):
    assistencia_juridica = db.session.query(AssistenciaJudiciaria).filter_by(
        id=id_assistencia_judiciaria,
        status=True
    ).first()
    
    if not assistencia_juridica:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    
    form = AssistenciaJudiciariaForm()
    
    if form.validate_on_submit():
        assistencia_juridica.nome = form.nome.data
        assistencia_juridica.regiao = form.regiao.data
        assistencia_juridica.setAreas_atendidas(form.areas_atendidas.data)
        assistencia_juridica.telefone = form.telefone.data
        assistencia_juridica.email = form.email.data
        assistencia_juridica.endereco.logradouro = form.logradouro.data
        assistencia_juridica.endereco.numero = form.numero.data
        assistencia_juridica.endereco.complemento = form.complemento.data
        assistencia_juridica.endereco.bairro = form.bairro.data
        assistencia_juridica.endereco.cep = form.cep.data
        assistencia_juridica.endereco.cidade = form.cidade.data
        assistencia_juridica.endereco.estado = form.estado.data
        
        db.session.commit()
        flash("Assistência judiciária editada com sucesso!", "success")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    
    # Pre-fill form with existing data
    form.nome.data = assistencia_juridica.nome
    form.regiao.data = assistencia_juridica.regiao
    form.areas_atendidas.data = assistencia_juridica.getAreas_atendidas()
    form.telefone.data = assistencia_juridica.telefone
    form.email.data = assistencia_juridica.email
    form.logradouro.data = assistencia_juridica.endereco.logradouro
    form.numero.data = assistencia_juridica.endereco.numero
    form.complemento.data = assistencia_juridica.endereco.complemento
    form.bairro.data = assistencia_juridica.endereco.bairro
    form.cep.data = assistencia_juridica.endereco.cep
    form.cidade.data = assistencia_juridica.endereco.cidade
    form.estado.data = assistencia_juridica.endereco.estado
    
    return render_template("editar_assistencia_juridica.html", form=form)


@plantao.route("/buscar_assistencia_judiciaria", methods=["POST"])
@login_required()
def buscar_assistencia_judiciaria():
    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    
    assistencias = db.session.query(AssistenciaJudiciaria).filter(
        AssistenciaJudiciaria.status == True,
        AssistenciaJudiciaria.nome.ilike(f"%{termo}%")
    ).order_by(
        AssistenciaJudiciaria.nome
    ).paginate(
        page=page,
        per_page=app.config["ATENDIDOS_POR_PAGINA"],
        error_out=False
    )
    
    return render_template(
        "lista_assistencia_judiciaria.html",
        assistencias=assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria
    )


@plantao.route("/buscar_orientacao_juridica", methods=["POST"])
@login_required()
def buscar_orientacao_juridica():
    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    
    orientacoes = db.session.query(OrientacaoJuridica).filter(
        OrientacaoJuridica.status == True,
        OrientacaoJuridica.area_direito.ilike(f"%{termo}%")
    ).order_by(
        OrientacaoJuridica.id.desc()
    ).paginate(
        page=page,
        per_page=app.config["ATENDIDOS_POR_PAGINA"],
        error_out=False
    )
    
    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


@plantao.route("/buscar_atendido", methods=["POST"])
@login_required()
def buscar_atendido():
    termo = request.form.get("termo", "")
    page = request.args.get("page", 1, type=int)
    
    atendidos = db.session.query(Atendido).filter(
        Atendido.status == True,
        Atendido.nome.ilike(f"%{termo}%")
    ).order_by(
        Atendido.nome
    ).paginate(
        page=page,
        per_page=app.config["ATENDIDOS_POR_PAGINA"],
        error_out=False
    )
    
    return render_template("lista_atendidos.html", atendidos=atendidos)
