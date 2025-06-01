from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
import pytz
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    json,
)
from flask_login import current_user

from gestaolegal import app, db, login_required
from gestaolegal.plantao.forms import (
    CadastroAtendidoForm,
    EditarAssistidoForm,
    OrientacaoJuridicaForm,
    TornarAssistidoForm,
    AssistenciaJudiciariaForm,
    CadastroOrientacaoJuridicaForm,
    AbrirPlantaoForm,
    SelecionarDuracaoPlantaoForm,
    FecharPlantaoForm,
)
from gestaolegal.plantao.models import (
    Assistido,
    AssistidoPessoaJuridica,
    Atendido,
    OrientacaoJuridica,
    AssistenciaJudiciaria,
    AssistenciaJudiciaria_xOrientacaoJuridica,
    Atendido_xOrientacaoJuridica,
    DiasMarcadosPlantao,
    DiaPlantao,
    Plantao,
    area_atuacao,
    beneficio,
    contribuicao_inss,
    enquadramento,
    escolaridade,
    RegistroEntrada,
    FilaAtendidos,
    moradia,
    orgao_reg,
    participacao_renda,
    qual_pessoa_doente,
    regiao_bh,
)
from gestaolegal.plantao.views_util import *
from gestaolegal.usuario.models import (
    Endereco,
    Usuario,
    sexo_usuario,
    usuario_urole_roles,
    usuario_urole_inverso,
)
from gestaolegal.utils.models import queryFiltradaStatus
from gestaolegal.notificacoes.models import Notificacao, acoes

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
    def validaDadosForm(form: CadastroAtendidoForm):
        emailRepetido = Atendido.query.filter_by(email=form.email.data).first()

        if not form.validate():
            return False
        # if emailRepetido:
        #     flash("Este email já está em uso.", "warning")
        #     return False
        return True

    def CriaAtendido(form: CadastroAtendidoForm):
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

        if not validaDadosForm(form):
            return render_template("cadastro_novo_atendido.html", form=form)

        db.session.add(CriaAtendido(form))
        db.session.commit()

        flash("Atendido cadastrado!", "success")
        _id = Atendido.query.filter_by(email=form.email.data).first().id
        return redirect(url_for("plantao.perfil_assistido", _id=_id))

    return render_template("cadastro_novo_atendido.html", form=form)


@plantao.route("/busca_atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def busca_atendidos_assistidos():
    page = request.args.get("page", 1, type=int)
    tipo_busca = request.args.get(
        "tipo_busca", tipos_busca_atendidos["TODOS"], type=str
    )
    busca = request.args.get("valor_busca", "", type=str)
    if tipo_busca == tipos_busca_atendidos["TODOS"]:
        atendidos_assistidos = busca_todos_atendidos_assistidos(busca, page)
    elif tipo_busca == tipos_busca_atendidos["ATENDIDOS"]:
        atendidos_assistidos = (
            Atendido.query.filter(
                (
                    (Atendido.nome.contains(busca))
                    | (Atendido.cpf.contains(busca))
                    | (Atendido.cnpj.contains(busca))
                )
                & (Atendido.status == True)
            )
            .outerjoin(Assistido)
            .filter(Assistido.atendido == None)
            .order_by(Atendido.nome)
            .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
        )
        atendidos_assistidos.items = [(x, None) for x in atendidos_assistidos.items]
    elif tipo_busca == tipos_busca_atendidos["ASSISTIDOS"]:
        atendidos_assistidos = (
            db.session.query(Atendido, Assistido)
            .filter(
                (
                    (Atendido.nome.contains(busca))
                    | (Atendido.cpf.contains(busca))
                    | (Atendido.cnpj.contains(busca))
                )
                & (Atendido.status == True)
            )
            .outerjoin(Assistido)
            .filter(Assistido.atendido != None)
            .order_by(Atendido.nome)
            .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
        )

    return render_template(
        "busca_atendidos.html",
        atendidos_assistidos=atendidos_assistidos,
        tipos_busca_atendidos=tipos_busca_atendidos,
    )

@plantao.route("/atendidos_assistidos", methods=["GET", "POST"])
@login_required()
def listar_atendidos():
    page = request.args.get("page", 1, type=int)

    atendidos_assistidos = busca_todos_atendidos_assistidos("", page)

    return render_template(
        "lista_atendidos.html",
        atendidos_assistidos=atendidos_assistidos,
        tipos_busca_atendidos=tipos_busca_atendidos,
    )


### Dados do atendido
@plantao.route("/dados_atendido/<int:id>", methods=["GET"])
@login_required()
def dados_atendido(id):
    _atendido = Atendido.query.get_or_404(id)
    _form = CadastroAtendidoForm()
    setValoresFormAtendido(_atendido, _form)
    _form.id_atendido = _atendido.id
    return render_template("dados_atendido.html", form=_form)


####Excluir Atendido
@plantao.route("/excluir_atendido/", methods=["POST", "GET"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_atendido():
    page = request.args.get("page", 1, type=int)

    if request.method == "POST":
        form = request.form
        id = form["id"]
        entidade_atendido = Atendido.query.filter_by(id=id).first()

        if not entidade_atendido:
            flash("Este atendido não existe!", "warning")
            return redirect(url_for("plantao.listar_atendidos"))

        entidade_atendido.status = False
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
    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id=id_atendido, status=True).first()

    if not entidade_atendido:
        flash("Este atendido não existe!", "warning")
        return redirect(url_for("plantao.listar_atendidos"))

    form = CadastroAtendidoForm()
    if request.method == "POST":

        if not validaDadosEditar_atendidoForm(form, request.form["emailAtual"]):
            return render_template(
                "editar_atendido.html", atendido=entidade_atendido, form=form
            )

        setDadosAtendido(entidade_atendido, form)
        db.session.commit()
        flash("Atendido editado com sucesso!", "success")
        return redirect(url_for("plantao.listar_atendidos"))

    setValoresFormAtendido(entidade_atendido, form)

    return render_template(
        "editar_atendido.html", atendido=entidade_atendido, form=form
    )


@plantao.route("/tornar_assistido/<id_atendido>", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def tornar_assistido(id_atendido):
    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_atendido = Atendido.query.filter_by(id=id_atendido).first()
    atendidoRepetido = Assistido.query.filter_by(id_atendido=id_atendido).first()

    if not entidade_atendido:
        flash("Este atendido não existe!", "warning")
        return redirect(url_for("plantao.listar_atendidos"))

    if atendidoRepetido:
        flash("Este Assistido já existe!", "warning")
        return redirect(url_for("plantao.listar_atendidos"))

    form = TornarAssistidoForm()

    form.pj_constituida.data = (
        False if entidade_atendido.pj_constituida == "0" else True
    )

    if request.method == "POST": 
        if not form.validate():
            return render_template(
                "tornar_assistido.html", atendido=entidade_atendido, form=form
            )

        entidade_assistido = Assistido()
        entidade_assistido.id_atendido = id_atendido

        setDadosGeraisAssistido(entidade_assistido, form)

        db.session.add(entidade_assistido)
        db.session.commit()

        if entidade_atendido.pj_constituida == "1":
            entidade_assistidoPessoaJuridica = AssistidoPessoaJuridica()
            entidade_assistidoPessoaJuridica.id_assistido = entidade_assistido.id

            setDadosAssistidoPessoaJuridica(entidade_assistidoPessoaJuridica, form)

            db.session.add(entidade_assistidoPessoaJuridica)
            db.session.commit()

        flash("Assistido cadastrado com sucesso!", "success")

        return redirect(url_for("plantao.listar_atendidos"))

    return render_template(
        "tornar_assistido.html", atendido=entidade_atendido, form=form
    )


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
    def setValoresFormAssistido(
        entidade_assistido: Assistido, form: TornarAssistidoForm
    ):
        form.sexo.data = entidade_assistido.sexo
        form.raca.data = entidade_assistido.raca
        form.profissao.data = entidade_assistido.profissao
        form.rg.data = entidade_assistido.rg
        form.grau_instrucao.data = entidade_assistido.grau_instrucao
        form.salario.data = entidade_assistido.salario
        form.beneficio.data = entidade_assistido.beneficio
        form.contribui_inss.data = entidade_assistido.contribui_inss
        form.qtd_pessoas_moradia.data = entidade_assistido.qtd_pessoas_moradia
        form.renda_familiar.data = entidade_assistido.renda_familiar
        form.participacao_renda.data = entidade_assistido.participacao_renda
        form.tipo_moradia.data = entidade_assistido.tipo_moradia
        form.possui_outros_imoveis.data = entidade_assistido.possui_outros_imoveis
        form.possui_veiculos.data = entidade_assistido.possui_veiculos
        form.possui_veiculos_obs.data = entidade_assistido.possui_veiculos_obs
        form.doenca_grave_familia.data = entidade_assistido.doenca_grave_familia
        form.obs_assistido.data = entidade_assistido.obs
        form.quantos_veiculos.data = entidade_assistido.quantos_veiculos
        form.ano_veiculo.data = entidade_assistido.ano_veiculo
        form.pessoa_doente.data = entidade_assistido.pessoa_doente
        form.pessoa_doente_obs.data = entidade_assistido.pessoa_doente_obs
        form.gastos_medicacao.data = entidade_assistido.gastos_medicacao

    def setValoresFormAssistidoPessoaJuridica(
        entidade_assistido_pj: AssistidoPessoaJuridica, form: TornarAssistidoForm
    ):
        form.socios.data = entidade_assistido_pj.socios
        form.situacao_receita.data = entidade_assistido_pj.situacao_receita
        form.enquadramento.data = entidade_assistido_pj.enquadramento
        form.sede_bh.data = entidade_assistido_pj.sede_bh
        form.area_atuacao.data = entidade_assistido_pj.area_atuacao
        form.negocio_nascente.data = entidade_assistido_pj.negocio_nascente
        form.orgao_registro.data = entidade_assistido_pj.orgao_registro
        form.faturamento_anual.data = entidade_assistido_pj.faturamento_anual
        form.ultimo_balanco_neg.data = entidade_assistido_pj.ultimo_balanco_neg
        form.resultado_econ_neg.data = entidade_assistido_pj.resultado_econ_neg
        form.tem_funcionarios.data = entidade_assistido_pj.tem_funcionarios
        form.qtd_funcionarios.data = entidade_assistido_pj.qtd_funcionarios
        form.regiao_sede_bh.data = entidade_assistido_pj.regiao_sede_bh
        form.regiao_sede_outros.data = entidade_assistido_pj.regiao_sede_outros

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    entidade_assistido = (
        Assistido.query.filter_by(id_atendido=id_atendido)
        .outerjoin(Atendido)
        .filter_by(status=True)
        .first()
    )
    if not entidade_assistido:
        flash("Este assistido não existe!", "warning")
        return redirect(url_for("plantao.listar_atendidos"))

    entidade_assistido_pj = AssistidoPessoaJuridica.query.filter_by(
        id_assistido=entidade_assistido.id
    ).first()
    form = EditarAssistidoForm()
    if request.method == "POST":
        if not validaDadosEditar_atendidoForm(form, request.form["emailAtual"]):
            return render_template(
                "editar_assistido.html", atendido=entidade_assistido.atendido, form=form
            )

        setDadosGeraisAssistido(entidade_assistido, form)
        setDadosAtendido(entidade_assistido.atendido, form)
        if entidade_assistido.atendido.pj_constituida:
            if not entidade_assistido_pj:
                entidade_assistido_pj = AssistidoPessoaJuridica()
                entidade_assistido_pj.id_assistido = entidade_assistido.id
                setDadosAssistidoPessoaJuridica(entidade_assistido_pj, form)
                db.session.add(entidade_assistido_pj)
            else:
                setDadosAssistidoPessoaJuridica(entidade_assistido_pj, form)
        else:
            if entidade_assistido_pj:
                db.session.delete(entidade_assistido_pj)

        db.session.commit()
        flash("Assistido editado com sucesso!", "success")
        return redirect(url_for("plantao.listar_atendidos"))

    setValoresFormAtendido(entidade_assistido.atendido, form)
    setValoresFormAssistido(entidade_assistido, form)
    if entidade_assistido_pj:
        setValoresFormAssistidoPessoaJuridica(entidade_assistido_pj, form)

    return render_template(
        "editar_assistido.html", atendido=entidade_assistido.atendido, form=form
    )


@plantao.route("/cadastro_orientacao_juridica/", methods=["POST", "GET"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def cadastro_orientacao_juridica():
    def CriaOrientacao(form: CadastroOrientacaoJuridicaForm, id_usuario):
        entidade_orientacao = OrientacaoJuridica(
            area_direito=form.area_direito.data,
            descricao=form.descricao.data,
            data_criacao=datetime.now(tz=pytz.timezone("America/Sao_Paulo")),
            status=True,
            id_usuario=id_usuario
        )

        if len(entidade_orientacao.descricao) > 2000 :
            flash("A descrição da orientacao juridica não pode ter mais de 2000 caracteres", "warning")
            return redirect(url_for("casos.cadastro_orientacao_juridica"))

        entidade_orientacao.setSubAreas(
            form.area_direito.data, form.sub_area.data, form.sub_areaAdmin.data
        )
        return entidade_orientacao

    page = request.args.get("page", 1, type=int)
    form = CadastroOrientacaoJuridicaForm()
    if request.method == "POST":
        if not form.validate():
            return render_template("cadastro_orientacao_juridica.html", form=form)
        entidade_orientacao = CriaOrientacao(form, current_user.id)
        db.session.add(entidade_orientacao)
        db.session.commit()
        if request.form.get("listaAtendidos"):
            listaAtendidos = json.loads(request.form.get("listaAtendidos"))
        
            if len(listaAtendidos['id']) > 0:
                # Inserção de atendidos
                for id_atendido in listaAtendidos['id']:
                    entidade_atendido = Atendido.query.filter_by(id=int(id_atendido)).first()
                    # orientacao = OrientacaoJuridica.query.filter_by(id=id_orientacao).first()
                    entidade_atendido.orientacoesJuridicas.append(entidade_orientacao)
                    db.session.add(entidade_atendido)
                    db.session.commit()

        if request.form.get("encaminhar_outras_aj") == "True":
            aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
            aj_oj.id_orientacaoJuridica = entidade_orientacao.id
            aj_oj.id_assistenciaJudiciaria = int(request.form.get("assistencia_judiciaria"))
            db.session.add(aj_oj)
            db.session.commit()

        flash("Orientação jurídica cadastrada!", "success")
        return redirect(
            url_for(
                "plantao.perfil_oj",
                id=entidade_orientacao.id
            )
        )
            

        # return request.form.get("listaAtendidos")
        

            
        # return redirect(
        #     url_for(
        #         "plantao.associacao_orientacao_juridica",
        #         id_orientacao=entidade_orientacao.id,
        #         encaminhar_outras_aj=form.encaminhar_outras_aj.data,
        #     )
        # )

    return render_template("cadastro_orientacao_juridica.html", form=form)


@plantao.route(
    "/encaminha_assistencia_judiciaria/<int:id_orientacao>", methods=["POST", "GET"]
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def encaminha_assistencia_judiciaria(id_orientacao):
    assistencias_judiciarias = db.session.query(AssistenciaJudiciaria)
    orientacao_juridica = OrientacaoJuridica.query.filter(OrientacaoJuridica.id == id_orientacao).first()
    assistencias_judiciarias = query_filtro_assistencia_judiciaria(assistencias_judiciarias, orientacao_juridica.area_direito).all()

    if request.method == "POST":
        list_ids = request.form.getlist(
            "dados[]"
        )  # Recebendo a lista de id's da requisição ajax

        for item in list_ids:
            aj_oj = AssistenciaJudiciaria_xOrientacaoJuridica()
            aj_oj.id_orientacaoJuridica = id_orientacao
            aj_oj.id_assistenciaJudiciaria = item
            db.session.add(aj_oj)
            db.session.flush()

        db.session.commit()
        flash("Orientação encaminhada.", "success")
        return redirect(url_for("plantao.perfil_oj", id=id_orientacao))

    return render_template(
        "encaminha_assistencia_judiciaria.html",
        assistencias_judiciarias=assistencias_judiciarias,
        id_orientacao=id_orientacao,
    )


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
    q = request.args.get("q")

    if q == None:
        resultado_json = {"results": []}
    else:
        orientacao_juridica = OrientacaoJuridica.query.filter_by(
            id=orientacao_id
        ).first()

        relacoes_aj_oj = (
            db.session.query(
                AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria
            )
            .filter_by(id_orientacaoJuridica=orientacao_juridica.id)
            .all()
        )
        relacoes_aj_oj = [x[0] for x in relacoes_aj_oj]

        assistencias_judiciarias = AssistenciaJudiciaria.query.filter(
            AssistenciaJudiciaria.areas_atendidas.contains(
                orientacao_juridica.area_direito
            )
            & AssistenciaJudiciaria.nome.contains(q)
            & (AssistenciaJudiciaria.status == True)
            & (~AssistenciaJudiciaria.id.in_(relacoes_aj_oj))
        ).all()

        resultado_json = {
            "results": [
                {"id": aj.id, "text": aj.nome} for aj in assistencias_judiciarias
            ]
        }

    response = app.response_class(
        response=json.dumps(resultado_json), status=200, mimetype="application/json"
    )
    return response


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
    def associa_ajs_a_oj(lista_aj: list, id_orientacao: int):
        relacoes_aj_oj = (
            db.session.query(
                AssistenciaJudiciaria_xOrientacaoJuridica.id_assistenciaJudiciaria
            )
            .filter_by(id_orientacaoJuridica=id_orientacao)
            .all()
        )
        relacoes_aj_oj = [x[0] for x in relacoes_aj_oj]
        for id_aj in lista_aj:
            if not (int(id_aj) in relacoes_aj_oj):
                associacao = AssistenciaJudiciaria_xOrientacaoJuridica(
                    id_orientacaoJuridica=id_orientacao, id_assistenciaJudiciaria=id_aj
                )
                db.session.add(associacao)
                db.session.flush()

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################
    encaminhar_outras_aj = request.args.get("encaminhar_outras_aj", "False", type=str)
    page = request.args.get("page", 1, type=int)

    if request.method == "POST":
        lista_aj = request.form.getlist("id_multiselect_aj")
        entidade_atendido = Atendido.query.filter_by(id=id_atendido).first()

        orientacao = OrientacaoJuridica.query.filter_by(id=id_orientacao).first()

        if not entidade_atendido:
            flash("Este atendido não existe!", "warning")
            return redirect(
                url_for(
                    "plantao.associacao_orientacao_juridica",
                    id_orientacao=id_orientacao,
                    encaminhar_outras_aj=encaminhar_outras_aj,
                )
            )

        else:
            entidade_atendido.orientacoesJuridicas.append(orientacao)
            db.session.add(entidade_atendido)
            db.session.commit()
            flash(f"{entidade_atendido.nome} associado à Orientação Jurídica com sucesso!", "success")

            if lista_aj:
                associa_ajs_a_oj(lista_aj, id_orientacao)
                db.session.commit()

        return redirect(
            url_for(
                "plantao.associacao_orientacao_juridica",
                id_orientacao=id_orientacao,
                encaminhar_outras_aj=encaminhar_outras_aj,
            )
        )
    blacklist = Atendido.query.outerjoin(Atendido_xOrientacaoJuridica).filter(
        Atendido_xOrientacaoJuridica.id_orientacaoJuridica == id_orientacao,
        Atendido.status == True,
    )
    blacklist_ids = []
    for atendido in blacklist:
        blacklist_ids.append(atendido.id)
    lista = Atendido.query.filter(
        ~Atendido.id.in_(blacklist_ids), Atendido.status == True
    ).paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
    orientacao_entidade = OrientacaoJuridica.query.get(id_orientacao)

    return render_template(
        "associa_orientacao_juridica.html",
        lista=lista.items,
        pagination=lista,
        orientacao_entidade=orientacao_entidade,
        encaminhar_outras_aj=encaminhar_outras_aj,
    )
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
    entidade_atendido = Atendido.query.filter_by(id=id_atendido).first()
    orientacao = OrientacaoJuridica.query.filter_by(id=id_orientacao).first()

    entidade_atendido.orientacoesJuridicas.remove(orientacao)
    db.session.commit()
    flash(f"{entidade_atendido.nome} removido da Orientação Jurídica com sucesso.", "success")

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

    encaminhar_outras_aj = request.args.get("encaminhar_outras_aj")
    id_orientacao_entidade = request.args.get("id_orientacao_entidade")

    orientacao_entidade = OrientacaoJuridica.query.get(id_orientacao_entidade)

    blacklist = Atendido.query.outerjoin(Atendido_xOrientacaoJuridica).filter(
        Atendido_xOrientacaoJuridica.id_orientacaoJuridica == id_orientacao_entidade
    )
    blacklist_ids = []
    for atendido in blacklist:
        blacklist_ids.append(atendido.id)

    if _busca is None:
        atendidos = Atendido.query.filter(
            ~Atendido.id.in_(blacklist_ids), Atendido.status == True
        )
    else:
        atendidos = Atendido.query.filter(
            (~Atendido.id.in_(blacklist_ids) & Atendido.status == True)
            & ((Atendido.nome.contains(_busca)) | (Atendido.cpf.contains(_busca)))
        )

    return render_template(
        "busca_associa_orientacao_juridica.html",
        lista=atendidos,
        orientacao_entidade=orientacao_entidade,
        encaminhar_outras_aj=encaminhar_outras_aj,
    )


@plantao.route("/excluir_orientacao_juridica/", methods=["POST"])
@login_required(role=[usuario_urole_roles["ADMINISTRADOR"][0]])
def excluir_oj():
    id = request.form["id"]
    entidade = OrientacaoJuridica.query.get_or_404(int(id))
    entidade.status = False
    db.session.add(entidade)
    db.session.commit()
    flash("orientação jurídica excluída.", "success")
    return redirect(url_for("plantao.orientacoes_juridicas"))


@plantao.route("/perfil_assistido/<int:_id>", methods=["GET"])
@login_required()
def perfil_assistido(_id):
    assistido = (
        queryFiltradaStatus(Atendido)
        .filter(Atendido.id == _id)
        .add_entity(Assistido)
        .add_entity(AssistidoPessoaJuridica)
        .outerjoin(Assistido, Assistido.id_atendido == Atendido.id)
        .outerjoin(
            AssistidoPessoaJuridica,
            AssistidoPessoaJuridica.id_assistido == Assistido.id,
        )
        .first()
    )

    dados_atendimento = {
        "Nome": assistido.Atendido.nome,
        "Data de Nascimento": assistido.Atendido.data_nascimento.strftime("%d/%m/%Y"),
        "CPF": assistido.Atendido.cpf,
        "CNPJ": assistido.Atendido.cnpj,
        "Celular": assistido.Atendido.celular,
        "E-mail": assistido.Atendido.email
    }

    dados_assistido = {
        "Sexo": next(sex[1] for sex in sexo_usuario.values() if sex[0] == assistido.Assistido.sexo),
        "Profissão": assistido.Assistido.profissao,
        "Raça": assistido.Assistido.raca,
        "RG": assistido.Assistido.rg,
        "Grau de Instrução": next(esc[1] for esc in escolaridade.values() if esc[0] == assistido.Assistido.grau_instrucao),
        "Salário": "R$ " + str(assistido.Assistido.salario).replace(".", ",")
    } if assistido.Assistido else None

    dados_pj = {
        "Situação Receita": assistido.AssistidoPessoaJuridica.situacao_receita,
        "Enquadramento": next(enq[1] for enq in enquadramento.values() if enq[0] == assistido.AssistidoPessoaJuridica.enquadramento),
        "Area de Atuação": next(area[1] for area in area_atuacao.values() if area[0] == assistido.AssistidoPessoaJuridica.area_atuacao),
        "Órgão de Registro": next(org[1] for org in orgao_reg.values() if org[0] == assistido.AssistidoPessoaJuridica.orgao_registro),
        "Faturamento Anual": "R$ " + str(assistido.AssistidoPessoaJuridica.faturamento_anual).replace(".", ",")
    } if assistido.AssistidoPessoaJuridica else None

    dados_endereco = {
        "Logradouro": assistido.Atendido.endereco.logradouro,
        "Número": assistido.Atendido.endereco.numero,
        "Complemento": assistido.Atendido.endereco.complemento,
        "Bairro": assistido.Atendido.endereco.bairro,
        "CEP": assistido.Atendido.endereco.cep,
        "Cidade": assistido.Atendido.endereco.cidade + ", " + assistido.Atendido.endereco.estado
    }

    dados_renda = {
        "Benefício Social": next(ben[1] for ben in beneficio.values() if ben[0] == assistido.Assistido.beneficio),
        "Contribui para a previdência social": next(cont[1] for cont in contribuicao_inss.values() if cont[0] == assistido.Assistido.contribui_inss),
        "Quantidade de pessoas que moram na mesma casa": assistido.Assistido.qtd_pessoas_moradia,
        "Renda Familiar": "R$ " + str(assistido.Assistido.renda_familiar).replace(".", ","),
        "Posição em relação à renda familiar": next(part[1] for part in participacao_renda.values() if part[0] == assistido.Assistido.participacao_renda),
        "Residência": next(mor[1] for mor in moradia.values() if mor[0] == assistido.Assistido.tipo_moradia),
        "Possui outros imóveis": "Sim" if assistido.Assistido.possui_outros_imoveis else "Não",
        "Possui veículos": "Sim" if assistido.Assistido.possui_veiculos else "Não"
    } if assistido.Assistido else None

    if assistido.Assistido and assistido.Assistido.possui_veiculos:
        dados_renda = dados_renda | {
        "Veículo": assistido.Assistido.possui_veiculos_obs,
        "Quantidade de Veículos": assistido.Assistido.quantos_veiculos,
        "Ano do Veículo": assistido.Assistido.ano_veiculo
        }

        doenca_resposta = "Sim" if assistido.Assistido.doenca_grave_familia == 'sim' else  ("Não" if assistido.Assistido.doenca_grave_familia == 'nao' else "Não Informou")

        dados_renda = dados_renda | {
        "Há pessoas com doença grave na família?": doenca_resposta
        }

        if assistido.Assistido.doenca_grave_familia == 'sim':
            dados_renda = dados_renda | {
            "Pessoa doente": next(pess[1] for pess in qual_pessoa_doente.values() if pess[0] == assistido.Assistido.pessoa_doente),
            "Gasto em medicamentos": "R$ " + str(assistido.Assistido.gastos_medicacao).replace(".", ",")
        }

        dados_renda = dados_renda | {
            "Observações": assistido.Assistido.obs
        }

    if assistido.AssistidoPessoaJuridica:
        dados_juridicos = {
            "Enquadramento": next(enq[1] for enq in enquadramento.values() if enq[0] == assistido.AssistidoPessoaJuridica.enquadramento),
            "Sócios da Pessoa Jurídica": assistido.AssistidoPessoaJuridica.socios,
            "Situação perante a Receita Federal": assistido.AssistidoPessoaJuridica.situacao_receita,
            "Sede constituída ou a constituir em Belo Horizonte?": "Sim" if assistido.AssistidoPessoaJuridica.sede_bh else "Não"
        }

        if assistido.AssistidoPessoaJuridica.sede_bh:
            local_sede = next(reg[1] for reg in regiao_bh.values() if reg[0] == assistido.AssistidoPessoaJuridica.regiao_sede_bh)
        else:
            local_sede = assistido.AssistidoPessoaJuridica.regiao_sede_outros

        dados_juridicos.update({
            "Local da Sede": local_sede,
            "Área de atuação": next(area[1] for area in area_atuacao.values() if area[0] == assistido.AssistidoPessoaJuridica.area_atuacao),
            "É negócio nascente?": "Sim" if assistido.AssistidoPessoaJuridica.negocio_nascente else "Não",
            "Órgão competente": next(org[1] for org in orgao_reg.values() if org[0] == assistido.AssistidoPessoaJuridica.orgao_registro),
            "Faturamento anual": "R$ " + str(assistido.AssistidoPessoaJuridica.faturamento_anual).replace(".", ",")
        })

        balanco_resposta = "Sim" if assistido.AssistidoPessoaJuridica.ultimo_balanco_neg == '1' else \
                      "Não" if assistido.AssistidoPessoaJuridica.ultimo_balanco_neg == '0' else "Não se aplica"

        resultado_resposta = "Sim" if assistido.AssistidoPessoaJuridica.resultado_econ_neg == "sim" else \
                         "Não" if assistido.AssistidoPessoaJuridica.resultado_econ_neg == "nao" else "Não se Aplica"

        funcionarios_resposta = "Sim" if assistido.AssistidoPessoaJuridica.tem_funcionarios == "sim" else \
                            "Não" if assistido.AssistidoPessoaJuridica.tem_funcionarios == "nao" else "Não se Aplica"

        dados_juridicos.update({
            "O balanço patrimonial do último ano foi negativo?": balanco_resposta,
            "O resultado econômico do último ano foi negativo?": resultado_resposta,
            "Tem funcionários?": funcionarios_resposta
        })

        if assistido.AssistidoPessoaJuridica.tem_funcionarios == 'sim':
            dados_juridicos["Quantidade de Funcionários"] = assistido.AssistidoPessoaJuridica.qtd_funcionarios
    else:
        dados_juridicos = None

    orientacoes: dict[str, str] | str = {}
    if assistido.Atendido.orientacoesJuridicas:
        for i, orientacao in enumerate(assistido.Atendido.orientacoesJuridicas, 1):
            key = f"Orientação {i}"
            value = f"{orientacao.area_direito.capitalize()} - {orientacao.data_criacao.strftime('%d/%m/%Y')}"
            value = f"<a href='/plantao/orientacao_juridica/{orientacao.id}' target='_blank'>{value}</a>"
            orientacoes[key] = value
    else:
        orientacoes = "Não há nenhuma orientação jurídica vinculada"

    casos: dict[str, str] | str = {}
    if assistido.Atendido.casos and assistido.Assistido:
        for i, caso in enumerate(assistido.Atendido.casos, 1):
            key = f"Caso {i}"
            value = f"{caso.area_direito.capitalize()}"
            if caso.sub_area:
                value += f" - {caso.sub_area.capitalize()}"
            value = f"<a href='/casos/visualizar/{caso.id}' target='_blank'>{value}</a>"
            casos[key] = value

    else:
        casos = "Não há nenhum caso vinculado"

    if assistido.Assistido:
        cards = [
            CardInfo("Dados de Atendimento", dados_atendimento),
            CardInfo("Dados de Assistido", dados_assistido),
            CardInfo("Dados PJ", dados_pj),
            CardInfo("Orientações Jurídicas", orientacoes),
            CardInfo("Casos Vinculados", casos),
            CardInfo("Endereço", dados_endereco),
            CardInfo("Renda e Patrimônio", dados_renda),
            CardInfo("Dados Juridicos", dados_juridicos)
        ]
    else:
        cards = [
            CardInfo("Dados de Atendimento", dados_atendimento),
            CardInfo("Endereço", dados_endereco),
            CardInfo("Orientações Jurídicas", orientacoes),
        ]

    return render_template(
        "perfil_assistidos.html",
        assistido=assistido,
        cards=cards
    )


############################################# ASSISTÊNCIA JUDICIÁRIA ##############################################################


@plantao.route("/nova_assistencia_judiciaria/", methods=["GET", "POST"])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
        usuario_urole_roles["PROFESSOR"][0],
    ]
)
def nova_assistencia_judiciaria():
    def setAssistenciaJudiciaria(form: AssistenciaJudiciariaForm):
        endereco = Endereco(
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cep=form.cep.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
        )
        db.session.add(endereco)
        db.session.flush()

        saida = AssistenciaJudiciaria(
            nome=form.nome.data,
            regiao=form.regiao.data,
            endereco_id=endereco.id,
            telefone=form.telefone.data,
            email=form.email.data,
            status=True,
        )

        saida.setAreas_atendidas(form.areas_atendidas.data)

        return saida

    _form = AssistenciaJudiciariaForm()
    if _form.validate_on_submit():
        entidade = setAssistenciaJudiciaria(_form)
        db.session.add(entidade)
        db.session.commit()
        flash("Assistência judiciária criada com sucesso!", "success")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    else:
        return render_template("cadastro_assistencia_judiciaria.html", form=_form)


@plantao.route(
    "/editar_assistencia_judiciaria/<int:id_assistencia_judiciaria>",
    methods=["POST", "GET"],
)
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["PROFESSOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
        usuario_urole_roles["COLAB_EXTERNO"][0],
    ]
)
def editar_assistencia_judiciaria(id_assistencia_judiciaria):
    def setDadosAssistenciaJudiciaria(
        form: AssistenciaJudiciariaForm, assistenciaJuridica: AssistenciaJudiciaria
    ):
        assistenciaJuridica.nome = form.nome.data
        assistenciaJuridica.regiao = form.regiao.data
        assistenciaJuridica.setAreas_atendidas(form.areas_atendidas.data)
        assistenciaJuridica.telefone = form.telefone.data
        assistenciaJuridica.email = form.email.data
        assistenciaJuridica.endereco.logradouro = form.logradouro.data
        assistenciaJuridica.endereco.numero = form.numero.data
        assistenciaJuridica.endereco.complemento = form.complemento.data
        assistenciaJuridica.endereco.bairro = form.bairro.data
        assistenciaJuridica.endereco.cep = form.cep.data
        assistenciaJuridica.endereco.cidade = form.cidade.data
        assistenciaJuridica.endereco.estado = form.estado.data

    def setAssistenciaJuridicaForm(
        form: AssistenciaJudiciariaForm, assistenciaJuridica: AssistenciaJudiciaria
    ):
        form.nome.data = assistenciaJuridica.nome
        form.regiao.data = assistenciaJuridica.regiao
        form.areas_atendidas.data = assistenciaJuridica.getAreas_atendidas()
        form.telefone.data = assistenciaJuridica.telefone
        form.email.data = assistenciaJuridica.email

        form.logradouro.data = assistenciaJuridica.endereco.logradouro
        form.numero.data = assistenciaJuridica.endereco.numero
        form.complemento.data = assistenciaJuridica.endereco.complemento
        form.bairro.data = assistenciaJuridica.endereco.bairro
        form.cep.data = assistenciaJuridica.endereco.cep
        form.cidade.data = assistenciaJuridica.endereco.cidade
        form.estado.data = assistenciaJuridica.endereco.estado

    ############################################# IMPLEMENTAÇÃO DA ROTA ##############################################################

    assistencia_juridica = AssistenciaJudiciaria.query.filter_by(
        id=id_assistencia_judiciaria, status=True
    ).first()
    form = AssistenciaJudiciariaForm()

    if not assistencia_juridica:
        flash("Assistência judiciária não encontrada!", "warning")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))

    if form.validate_on_submit():
        setDadosAssistenciaJudiciaria(form, assistencia_juridica)
        db.session.commit()
        flash("Assistência judiciária editada com sucesso!", "success")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))

    setAssistenciaJuridicaForm(form, assistencia_juridica)

    return render_template("editar_assistencia_juridica.html", form=form)


# Rota de teste da Visualização da assistência judiciária
@plantao.route("/assistencias_judiciarias/", methods=["POST", "GET"])
@login_required()
def listar_assistencias_judiciarias():
    page = request.args.get("page", 1, type=int)

    _assistencias = (
        AssistenciaJudiciaria.query.filter_by(status=True)
        .order_by("nome")
        .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
    )

    return render_template(
        "lista_assistencia_judiciaria.html",
        assistencias=_assistencias,
        filtro_busca_assistencia_judiciaria=filtro_busca_assistencia_judiciaria,
    )


# Página de orientações jurídicas
@plantao.route("/orientacoes_juridicas")
@login_required()
def orientacoes_juridicas():
    page = request.args.get("page", 1, type=int)
    orientacoes = (
        OrientacaoJuridica.query.filter_by(status=True)
        .order_by(OrientacaoJuridica.id.desc())
        .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
    )

    return render_template("orientacoes_juridicas.html", orientacoes=orientacoes)


# Perfil de orientações jurídicas
@plantao.route("/orientacao_juridica/<id>")
@login_required()
def perfil_oj(id):
    _orientacao = OrientacaoJuridica.query.get_or_404(id)
    atendidos_envolvidos = (
        queryFiltradaStatus(Atendido)
        .outerjoin(Atendido_xOrientacaoJuridica)
        .filter(Atendido_xOrientacaoJuridica.id_orientacaoJuridica == _orientacao.id)
        .order_by(Atendido.nome)
        .all()
    )
    if _orientacao.id_usuario:
        usuario = Usuario.query.filter(Usuario.id == _orientacao.id_usuario).first()
    else:
        usuario = {"nome": "--"}
    assistencias_envolvidas = AssistenciaJudiciaria_xOrientacaoJuridica.query.filter_by(
        id_orientacaoJuridica=_orientacao.id
    ).all()

    return render_template(
        "perfil_orientacao_juridica.html",
        orientacao=_orientacao,
        atendidos=atendidos_envolvidos,
        assistencias=assistencias_envolvidas,
        usuario=usuario
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

    entidade_orientacao = OrientacaoJuridica.query.filter_by(
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
            .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
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
            .paginate(page, app.config["ATENDIDOS_POR_PAGINA"], False)
        )

    return render_template("busca_orientacoes_juridicas.html", orientacoes=orientacoes)


# Excluir assistência judiciária
@plantao.route("/excluir_assistencia_judiciaria/<_id>")
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["COLAB_PROJETO"][0],
    ]
)
def excluir_assistencia_judiciaria(_id):
    aj = db.session.query(AssistenciaJudiciaria).filter_by(id=_id).first()
    if aj is None:
        flash("Assistência judiciária não encontrada.", "warning")
        return redirect(url_for("plantao.listar_assistencias_judiciarias"))
    aj.status = False
    db.session.add(aj)
    db.session.commit()
    flash("Assistência judiciária excluída com sucesso.", "success")
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
        page, app.config["ATENDIDOS_POR_PAGINA"], False
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
    dias_usuario_marcado = DiasMarcadosPlantao.query.filter_by(
        id_usuario=current_user.id, status = True, 
    ).all()

    plantao = Plantao.query.first()
    apaga_dias_marcados(plantao, dias_usuario_marcado)
    try:
        if (
            not (
                current_user.urole
                in [
                    usuario_urole_roles["ADMINISTRADOR"][0],
                    usuario_urole_roles["COLAB_PROJETO"][0],
                ]
            )
        ) and (plantao.data_abertura == None):
            flash("O plantão não está aberto!")
            return redirect(url_for("principal.index"))

        dias_usuario_atual = DiasMarcadosPlantao.query.filter_by(
            id_usuario=current_user.id, status = True,
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

    datas_ja_marcadas = DiasMarcadosPlantao.query.filter(DiasMarcadosPlantao.status == True).all()
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

    dias_duracao_gravados = DiaPlantao.query.filter(DiaPlantao.status == True).all()
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

    plantao = Plantao.query.first()
    valida_fim_plantao(plantao)
    if (
        not (
            current_user.urole
            in [
                usuario_urole_roles["ADMINISTRADOR"][0],
                usuario_urole_roles["COLAB_PROJETO"][0],
            ]
        )
    ) and (plantao.data_abertura == None):
        flash("O plantão não está aberto!")
        return redirect(url_for("principal.index"))

    dias_abertos_plantao = DiaPlantao.query.filter_by(status=1).all()
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

    dias_usuario_marcado = DiasMarcadosPlantao.query.filter_by(
        id_usuario=current_user.id, status = True
    ).all()

    validacao = data_marcada in lista_dias_abertos
    if not validacao:
        tipo_mensagem = "warning"
        mensagem = "Data selecionada não foi aberta para plantão."
        resultado_json = cria_json(
            render_template("lista_datas_plantao.html", data_atual=data_atual, datas_plantao=dias_usuario_marcado),
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
            render_template("lista_datas_plantao.html", datas_plantao=dias_usuario_marcado, data_atual=data_atual),
            mensagem,
            tipo_mensagem,
        )
        return app.response_class(
            response=json.dumps(resultado_json), status=200, mimetype="application/json"
        )

    if len(dias_usuario_marcado) >= 2 or (len(dias_usuario_marcado) >= 1 and current_user.urole == usuario_urole_roles['ORIENTADOR'][0]):
        tipo_mensagem = "warning"
        mensagem = "Você atingiu o limite de plantões cadastrados."
        resultado_json = cria_json(
            render_template("lista_datas_plantao.html", datas_plantao=dias_usuario_marcado, data_atual=data_atual),
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
            render_template("lista_datas_plantao.html", datas_plantao=dias_usuario_marcado, data_atual=data_atual),
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
    dias_usuario_atual = DiasMarcadosPlantao.query.filter_by(
        id_usuario=current_user.id, status=True
    ).all()
    resultado_json = cria_json(
        render_template("lista_datas_plantao.html", datas_plantao=dias_usuario_atual, data_atual=data_atual),
        mensagem,
        tipo_mensagem,
    )
    return app.response_class(
        response=json.dumps(resultado_json), status=200, mimetype="application/json"
    )


@plantao.route("/editar_plantao", methods=["GET"])
@login_required()
def editar_plantao():
    dias_marcados_plantao = DiasMarcadosPlantao.query.filter_by(
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

    dias_abertos_plantao = DiaPlantao.query.filter_by(status=1).all()
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

    dias_abertos_plantao = DiaPlantao.query.filter_by(status=1).all()
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

    verifica_historico = RegistroEntrada.query.filter(
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

    verifica_historico = RegistroEntrada.query.filter(
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
                plantao = DiasMarcadosPlantao.query.get_or_404(int(tipo_confirmacao[1]))
                plantao.confirmacao = dados[i][1]

                db.session.commit()

            else:
                presenca = RegistroEntrada.query.get_or_404(int(tipo_confirmacao[1]))
                presenca.confirmacao = dados[i][1]

                db.session.commit()

    if (
        date.today().weekday() != 1
    ):  # Se for um dia diferente de segunda, lista as presencas de ontem
        data_ontem = date.today() - timedelta(days=1)

        presencas_registradas = RegistroEntrada.query.filter(
            RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
        ).all()
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = DiasMarcadosPlantao.query.filter(
            DiasMarcadosPlantao.data_marcada == data_ontem,
            DiasMarcadosPlantao.confirmacao == "aberto",
        ).all()

    else:
        data_ontem = date.today() - timedelta(
            days=3
        )  # Se for segunda, lista as presenças

        presencas_registradas = RegistroEntrada.query.filter(
            RegistroEntrada.status == False
        ).all()
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = DiasMarcadosPlantao.query.filter(
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

    presencas_registradas = RegistroEntrada.query.filter(
        RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
    ).all()
    presencas = [
        presenca
        for presenca in presencas_registradas
        if presenca.data_entrada.date() == data_procurada
    ]

    plantoes_marcados = DiasMarcadosPlantao.query.filter(
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

    plantao = Plantao.query.first()

    valida_fim_plantao(plantao)
    if (
        not (
            current_user.urole
            in [
                usuario_urole_roles["ADMINISTRADOR"][0],
                usuario_urole_roles["COLAB_PROJETO"][0],
            ]
        )
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
        periodo=f"{hoje.month+1:02}/{hoje.year}",
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
    plantao = Plantao.query.first()

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
            if not (data in datas_duracao_banco_dados):
                nova_data = DiaPlantao(data=data)
                db.session.add(nova_data)
                db.session.flush()

        # Se dia do banco não estava no front, apagar no banco.
        for duracao in lista_duracao_banco_dados:
            if not (duracao[0] in datas_duracao):
                DiaPlantao.query.filter(DiaPlantao.id == duracao[1]).delete()
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
    if data['action'] == 'modal':
        entidade_assistido = Assistido()
        entidade_assistido.id_atendido = data['id_atendido']
        entidade_assistido.sexo = data['sexo']
        entidade_assistido.raca = data['raca']
        entidade_assistido.profissao = data['profissao']
        entidade_assistido.rg = data['rg']
        entidade_assistido.grau_instrucao = data['grau_instrucao']
        entidade_assistido.salario = data['salario']
        entidade_assistido.beneficio = data['beneficio']
        entidade_assistido.qual_beneficio = data['qual_beneficio']
        entidade_assistido.contribui_inss = data['contribui_inss']
        entidade_assistido.qtd_pessoas_moradia = data['qtd_pessoas_moradia']
        entidade_assistido.renda_familiar = data['renda_familiar']
        entidade_assistido.participacao_renda = data['participacao_renda']
        entidade_assistido.tipo_moradia = data['tipo_moradia']
        entidade_assistido.possui_outros_imoveis = True if data['possui_outros_imoveis'] == 'Não' else False
        entidade_assistido.quantos_imoveis = 0 if data['quantos_imoveis'] == "" else data['quantos_imoveis']
        entidade_assistido.possui_veiculos = True if data['possui_veiculos'] == 'Não' else False
        entidade_assistido.doenca_grave_familia = data['doenca_grave_familia']
        entidade_assistido.obs = data['obs_assistido']

        entidade_assistido.setCamposVeiculo(
            entidade_assistido.possui_veiculos,
            data['possui_veiculos_obs'],
            0 if data['quantos_veiculos'] == '' else data['quantos_veiculos'],
            data['ano_veiculo'],
        )
        entidade_assistido.setCamposDoenca(
            entidade_assistido.doenca_grave_familia,
            data['pessoa_doente'],
            data['pessoa_doente_obs'],
            0 if data['gastos_medicacao'] == '' else data['gastos_medicacao'],
        )
        db.session.add(entidade_assistido)
        db.session.commit()

        return json.dumps({"status": "success", "message": "Assistido cadastrado com sucesso!", 'id': data['id_atendido']})
    else:
        return json.dumps({"status": "error", "message": "Campo de ação não encontrado"})
    
@plantao.route("/verifica_assistido/<_id>", methods=[ "GET", "POST" ])
@login_required(
    role=[
        usuario_urole_roles["ADMINISTRADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]
)
def verifica_assistdo(_id):
    if request.method == "POST":
        return json.dumps({"hello": "world"})
    verificado = Assistido.query.filter(Assistido.id_atendido == _id).first()
    return json.dumps({"assistido": True if verificado else False})

@plantao.route("/fila-atendimento", methods=[ "GET", "POST" ])
@login_required()
def fila_atendimento():
    return render_template("lista_atendimentos.html")

@plantao.route("/fila-atendimento/criar", methods=[ "GET", "POST" ])
@login_required()
def criar_fila():
    if request.method == "GET":
        return json.dumps({"error": "error to access the page"})     
    data = request.get_json(silent=True, force=True)
    
    psicologia = data['psicologia']
    prioridade = data['prioridade']
    senha = data['senha']
    id_atendido = data['id_atendido']
    fila = FilaAtendidos()
    fila.psicologia=psicologia
    fila.prioridade=prioridade
    fila.data_criacao=datetime.now()
    fila.senha=senha
    fila.id_atendido=id_atendido
    fila.status=0
    db.session.add(fila)
    db.session.commit()
    return json.dumps({"message": "success" if fila.id else "error"})

@plantao.route("/fila-atendimento/gerar-senha/<prioridade>", methods=[ "GET" ])
@login_required()
def gerar_senha(prioridade):
    today = datetime.now()
    senha = len(
        FilaAtendidos.query.filter(FilaAtendidos.prioridade == prioridade, FilaAtendidos.data_criacao.between(today.strftime("%Y-%m-%d 00:00:00"), today.strftime("%Y-%m-%d 23:59:59"))).all()
        ) + 1
    senha = "0"+str(senha) if senha < 10 else str(senha)
    return json.dumps({"senha": senha})

@plantao.route("/fila-atendimento/hoje", methods=["GET", "PUT"])
@login_required()
def pegar_atendimentos():
    if request.method == "PUT":
        data = request.get_json(silent=True, force=True)
        id = data['id']
        fila = FilaAtendidos.query.filter(FilaAtendidos.id == id).first()
        fila.status = data['status']
        try:
            db.session.commit()
            return json.dumps({"message": "Status atualizado com sucesso"})
        except: 
            return json.dumps({"message": "Ocorreu um erro durante a atualização"})

    today = datetime.now()
    fila = FilaAtendidos.query.filter(
            FilaAtendidos.data_criacao.between(today.strftime("%Y-%m-%d 00:00:00"), today.strftime("%Y-%m-%d 23:59:59"))
        ).all()
    fila_obj = []
    for f in fila:
        fila_obj.append({
            "id": f.id,
            "nome": f.atendido.nome,
            "senha": f.senha,
            "hora": f.data_criacao,
            "prioridade": f.prioridade,
            "psicologia": "Sim" if f.psicologia else "Não",
            "status": f.status
        })
    return json.dumps(fila_obj)

@plantao.route("/atendido/fila-atendimento", methods=["GET","POST"])
@login_required()
def ajax_cadastrar_atendido():
    data = request.get_json(silent=True, force=True)
    # form = CadastroAtendidoForm()
    entidade_endereco = Endereco(
        logradouro=data['logradouro'],
        numero=data['numero'],
        complemento=data['complemento'],
        bairro=data['bairro'],
        cep=data['cep'],
        cidade=data['cidade'],
        estado=data['estado'],
    )
    db.session.add(entidade_endereco)
    db.session.flush()
    entidade_atendido = Atendido(
        nome=data['nome'],
        data_nascimento=data['data_nascimento'],
        cpf=data['cpf'],
        cnpj=data['cnpj'],
        telefone=data['telefone'],
        celular=data['celular'],
        email=data['email'],
        estado_civil=data['estado_civil'],
        como_conheceu=data['como_conheceu'],
        indicacao_orgao=data['indicacao_orgao'],
        procurou_outro_local=data['procurou_outro_local'],
        procurou_qual_local=data['procurou_qual_local'],
        obs=data['obs_atendido'],
        endereco_id=entidade_endereco.id,
        pj_constituida=1 if data['pj_constituida'] == "True" else 0,
        repres_legal=1 if data['repres_legal'] == "True" else 0,
        nome_repres_legal=data['nome_repres_legal'],
        cpf_repres_legal=data['cpf_repres_legal'],
        contato_repres_legal=data['contato_repres_legal'],
        rg_repres_legal=data['rg_repres_legal'],
        nascimento_repres_legal=data['nascimento_repres_legal'],
        pretende_constituir_pj=data['pretende_constituir_pj'],
        status=1,
    )
    entidade_atendido.setIndicacao_orgao(
        data['indicacao_orgao'], entidade_atendido.como_conheceu
    )
    entidade_atendido.setCnpj(
        entidade_atendido.pj_constituida, data['cnpj'], 1 if data['repres_legal'] else 0
    )

    entidade_atendido.setRepres_legal(
        entidade_atendido.repres_legal,
        entidade_atendido.pj_constituida,
        data['nome_repres_legal'],
        data['cpf_repres_legal'],
        data['contato_repres_legal'],
        data['rg_repres_legal'],
        data['nascimento_repres_legal'],
    )

    entidade_atendido.setProcurou_qual_local(
        entidade_atendido.procurou_outro_local, data['procurou_qual_local']
    )
    db.session.add(entidade_atendido)
    db.session.commit()
    return json.dumps({"id": entidade_atendido.id, "nome": entidade_atendido.nome})
