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
)
from flask_login import current_user

from gestaolegal import app, db, login_required
from gestaolegal.models.atendido import Atendido
from gestaolegal.models.endereco import Endereco
from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.notificacoes.models import Notificacao, acoes
from gestaolegal.plantao.forms import (
    AbrirPlantaoForm,
    FecharPlantaoForm,
    SelecionarDuracaoPlantaoForm,
)
from gestaolegal.plantao.models import (
    DiaPlantao,
    DiasMarcadosPlantao,
    FilaAtendidos,
    Plantao,
    RegistroEntrada,
)
from gestaolegal.plantao.views_util import *
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido
from gestaolegal.usuario.models import (
    usuario_urole_inverso,
    usuario_urole_roles,
)


@dataclass
class CardInfo:
    title: str
    body: dict[str, str | None] | str


plantao = Blueprint("plantao", __name__, template_folder="templates")

data_atual = datetime.now().date()


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
    id_orientacao_entidade = request.args.get("id_orientacao_entidade")
    encaminhar_outras_aj = request.args.get("encaminhar_outras_aj", "False")

    # Get the orientacao juridica
    orientacao_entidade = None
    if id_orientacao_entidade:
        orientacao_entidade = (
            db.session.query(OrientacaoJuridica)
            .filter_by(id=id_orientacao_entidade, status=True)
            .first()
        )

    query = db.session.query(Atendido).filter(Atendido.status == True)

    if _busca:
        query = query.filter(
            (Atendido.nome.ilike(f"%{_busca}%"))
            | (Atendido.cpf.ilike(f"%{_busca}%"))
            | (Atendido.cnpj.ilike(f"%{_busca}%"))
        )

    atendidos = query.order_by(Atendido.nome).paginate(
        page=page, per_page=app.config["ATENDIDOS_POR_PAGINA"], error_out=False
    )

    return render_template(
        "atendido/busca_associa_oj.html",
        atendidos=atendidos,
        busca=_busca,
        orientacao_entidade=orientacao_entidade,
        encaminhar_outras_aj=encaminhar_outras_aj,
    )


# Página de plantao
@plantao.route("/pagina_plantao", methods=["POST", "GET"])
@login_required()
def pg_plantao():
    dias_usuario_marcado = (
        db.session.query(DiasMarcadosPlantao)
        .filter_by(
            id_usuario=current_user.id,
            status=True,
        )
        .all()
    )

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

        dias_usuario_atual = (
            db.session.query(DiasMarcadosPlantao)
            .filter_by(
                id_usuario=current_user.id,
                status=True,
            )
            .all()
        )

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

    datas_ja_marcadas = (
        db.session.query(DiasMarcadosPlantao)
        .filter(DiasMarcadosPlantao.status == True)
        .all()
    )
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

    dias_duracao_gravados = (
        db.session.query(DiaPlantao).filter(DiaPlantao.status == True).all()
    )
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

    dias_usuario_marcado = (
        db.session.query(DiasMarcadosPlantao)
        .filter_by(id_usuario=current_user.id, status=True)
        .all()
    )

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
    dias_usuario_atual = (
        db.session.query(DiasMarcadosPlantao)
        .filter_by(id_usuario=current_user.id, status=True)
        .all()
    )
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
    dias_marcados_plantao = (
        db.session.query(DiasMarcadosPlantao)
        .filter_by(id_usuario=current_user.id, status=True)
        .all()
    )
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

    verifica_historico = (
        db.session.query(RegistroEntrada)
        .filter(
            RegistroEntrada.id_usuario == current_user.id,
            RegistroEntrada.status == True,
        )
        .first()
    )
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

    verifica_historico = (
        db.session.query(RegistroEntrada)
        .filter(
            RegistroEntrada.id_usuario == current_user.id,
            RegistroEntrada.status == True,
        )
        .first()
    )
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
                plantao = db.session.query(DiasMarcadosPlantao).get_or_404(
                    int(tipo_confirmacao[1])
                )
                plantao.confirmacao = dados[i][1]

                db.session.commit()

            else:
                presenca = db.session.query(RegistroEntrada).get_or_404(
                    int(tipo_confirmacao[1])
                )
                presenca.confirmacao = dados[i][1]

                db.session.commit()

    if (
        date.today().weekday() != 1
    ):  # Se for um dia diferente de segunda, lista as presencas de ontem
        data_ontem = date.today() - timedelta(days=1)

        presencas_registradas = (
            db.session.query(RegistroEntrada)
            .filter(
                RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
            )
            .all()
        )
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = (
            db.session.query(DiasMarcadosPlantao)
            .filter(
                DiasMarcadosPlantao.data_marcada == data_ontem,
                DiasMarcadosPlantao.confirmacao == "aberto",
            )
            .all()
        )

    else:
        data_ontem = date.today() - timedelta(
            days=3
        )  # Se for segunda, lista as presenças

        presencas_registradas = (
            db.session.query(RegistroEntrada)
            .filter(RegistroEntrada.status == False)
            .all()
        )
        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = (
            db.session.query(DiasMarcadosPlantao)
            .filter(
                DiasMarcadosPlantao.data_marcada == data_ontem,
                DiasMarcadosPlantao.confirmacao == "aberto",
            )
            .all()
        )

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

    presencas_registradas = (
        db.session.query(RegistroEntrada)
        .filter(
            RegistroEntrada.status == False, RegistroEntrada.confirmacao == "aberto"
        )
        .all()
    )
    presencas = [
        presenca
        for presenca in presencas_registradas
        if presenca.data_entrada.date() == data_procurada
    ]

    plantoes_marcados = (
        db.session.query(DiasMarcadosPlantao)
        .filter(
            DiasMarcadosPlantao.data_marcada == data_procurada,
            DiasMarcadosPlantao.confirmacao == "aberto",
        )
        .all()
    )

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
                db.session.query(DiaPlantao).filter(
                    DiaPlantao.id == duracao[1]
                ).delete()
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
    verificado = (
        db.session.query(Assistido).filter(Assistido.id_atendido == _id).first()
    )
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
            db.session.query(FilaAtendidos)
            .filter(
                FilaAtendidos.prioridade == prioridade,
                FilaAtendidos.data_criacao.between(
                    today.strftime("%Y-%m-%d 00:00:00"),
                    today.strftime("%Y-%m-%d 23:59:59"),
                ),
            )
            .all()
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
    fila = (
        db.session.query(FilaAtendidos)
        .filter(
            FilaAtendidos.data_criacao.between(
                today.strftime("%Y-%m-%d 00:00:00"), today.strftime("%Y-%m-%d 23:59:59")
            )
        )
        .all()
    )
    fila_obj = []
    for f in fila:
        fila_obj.append(
            {
                "id": f.id,
                "nome": f.atendido.nome,
                "cpf": f.atendido.cpf,
                "celular": f.atendido.celular,
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
