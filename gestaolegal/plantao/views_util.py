from datetime import date, datetime

from flask import flash, redirect, url_for
from flask_login import current_user

from gestaolegal import db
from gestaolegal.models.atendido import Atendido
from gestaolegal.plantao.forms import AbrirPlantaoForm, FecharPlantaoForm
from gestaolegal.plantao.models import (
    AssistenciaJudiciaria,
    DiaPlantao,
    DiasMarcadosPlantao,
    Plantao,
    assistencia_jud_areas_atendidas,
)
from gestaolegal.usuario.models import Usuario, usuario_urole_roles

##############################################################
################## CONSTANTES ################################
##############################################################

tipos_busca_atendidos = {
    "TODOS": "todos",
    "ATENDIDOS": "atendidos",
    "ASSISTIDOS": "assistidos",
}

filtro_busca_assistencia_judiciaria = assistencia_jud_areas_atendidas
filtro_busca_assistencia_judiciaria["TODAS"] = ("todas", "Todas")

##############################################################
################## FUNCOES ###################################
##############################################################


def validaDadosEditar_atendidoForm(form, emailAtual: str):
    emailRepetido = db.session.query(Atendido).filter_by(email=form.email.data).first()

    if not form.validate():
        return False
    if (emailRepetido) and (form.email.data != emailAtual):
        flash("Este email já está em uso.", "warning")
        return False
    return True


def serializar(lista):
    return [x.as_dict() for x in lista]


def numero_plantao_a_marcar(id_usuario: int):
    dias_marcados = (
        db.session.query(DiasMarcadosPlantao).filter_by(id_usuario=id_usuario).all()
    )
    return len(dias_marcados) + 1


def checa_vagas_em_todos_dias(dias_disponiveis: list, urole: str) -> bool:
    """
    Função que retorna verdadeiro caso NÃO exista vagas para um determinado tipo de usuario
    """
    if urole == usuario_urole_roles["ORIENTADOR"][0]:
        orientador_no_dia = []  # essa lista armazena se todos os dias tem ou nao um orientador ja cadastrado num dia, true caso sim e false do contrario
        for i in range(0, len(dias_disponiveis)):
            seletor_banco_de_dados = (
                db.session.query(DiasMarcadosPlantao)
                .filter_by(data_marcada=dias_disponiveis[i])
                .all()
            )
            for data in seletor_banco_de_dados:
                if data.usuario.urole == usuario_urole_roles["ORIENTADOR"][0]:
                    orientador_no_dia.append(True)
                    break

        if len(orientador_no_dia) < len(dias_disponiveis):
            return False
        else:
            return True
    else:
        tres_estagiarios_no_dia = []  # essa lista armazena se todos os dias tem ou nao 3 ou mais estagiarios ja cadastrados num dia, true caso sim e false do contrario
        for i in range(0, len(dias_disponiveis)):
            seletor_banco_de_dados = (
                db.session.query(DiasMarcadosPlantao)
                .filter_by(data_marcada=dias_disponiveis[i])
                .all()
            )
            numero_de_estagiarios_no_dia = 0
            for data in seletor_banco_de_dados:
                if data.usuario.urole == "estag_direito":
                    numero_de_estagiarios_no_dia += 1

            if numero_de_estagiarios_no_dia >= 3:
                tres_estagiarios_no_dia.append(True)
            else:
                tres_estagiarios_no_dia.append(False)

        if False in tres_estagiarios_no_dia:
            return False
        else:
            return True


def confirma_disponibilidade_dia(dias_disponiveis: list, data: date):
    """
    Função que retorna verdadeiro caso uma data esteja disponível para marcar um plantão.
    """

    urole_usuario = current_user.urole
    consulta_data_marcada = (
        db.session.query(DiasMarcadosPlantao).filter_by(data_marcada=data).all()
    )
    numero_orientador = 0
    numero_estagiario = 0

    for data in consulta_data_marcada:
        if data.usuario.urole == usuario_urole_roles["ORIENTADOR"][0]:
            numero_orientador += 1
        else:
            numero_estagiario += 1

    if (urole_usuario == usuario_urole_roles["ORIENTADOR"][0]) and (
        numero_orientador >= 1
    ):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False

    elif (urole_usuario == usuario_urole_roles["ESTAGIARIO_DIREITO"][0]) and (
        numero_estagiario >= 3
    ):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False
    else:
        return True


def resposta_configura_abertura() -> redirect:
    return redirect(url_for("plantao.pg_plantao"))


def atualiza_data_abertura(form: AbrirPlantaoForm, plantao: Plantao):
    data_escolhida = form.data_abertura.data
    hora_escolhida = form.hora_abertura.data

    plantao.data_abertura = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()


def atualiza_data_fechamento(form: FecharPlantaoForm, plantao: Plantao):
    data_escolhida = form.data_fechamento.data
    hora_escolhida = form.hora_fechamento.data

    plantao.data_fechamento = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()


def set_abrir_plantao_form(form: AbrirPlantaoForm, plantao: Plantao):
    if plantao:
        if plantao.data_abertura:
            form.data_abertura.data = plantao.data_abertura.date()
            form.hora_abertura.data = plantao.data_abertura.time()


def set_fechar_plantao_form(form: FecharPlantaoForm, plantao: Plantao):
    if plantao:
        if plantao.data_fechamento:
            form.data_fechamento.data = plantao.data_fechamento.date()
            form.hora_fechamento.data = plantao.data_fechamento.time()


def vagas_restantes(dias_disponiveis: list, data: date):
    num_max = 0
    if data not in dias_disponiveis:
        return 0
    for i in range(0, len(dias_disponiveis)):
        vagas_preenchidas = (
            db.session.query(DiasMarcadosPlantao, Usuario.urole)
            .select_from(DiasMarcadosPlantao)
            .join(Usuario)
            .filter(
                Usuario.urole == current_user.urole,
                DiasMarcadosPlantao.data_marcada == dias_disponiveis[i],
            )
            .all()
        )
        if len(vagas_preenchidas) > num_max:
            num_max = len(vagas_preenchidas)
        if current_user.urole == usuario_urole_roles["ORIENTADOR"][0]:
            if num_max < 1:
                num_max = 1
        if current_user.urole == usuario_urole_roles["ESTAGIARIO_DIREITO"][0]:
            if num_max < 3:
                num_max = 3
    vagas_no_dia = (
        db.session.query(DiasMarcadosPlantao, Usuario.urole)
        .select_from(DiasMarcadosPlantao)
        .join(Usuario)
        .filter(
            Usuario.urole == current_user.urole,
            DiasMarcadosPlantao.data_marcada == data,
        )
        .all()
    )
    if current_user.urole not in [
        usuario_urole_roles["ORIENTADOR"][0],
        usuario_urole_roles["ESTAGIARIO_DIREITO"][0],
    ]:
        return "Sem limites"
    else:
        return num_max - len(vagas_no_dia)


def valida_fim_plantao(plantao: Plantao):
    if plantao:
        if plantao.data_fechamento:
            if plantao.data_fechamento < datetime.now():
                try:
                    db.session.query(DiaPlantao).delete()
                    db.session.flush()

                    plantao.data_fechamento = None
                    plantao.data_abertura = None
                    db.session.commit()
                except:
                    db.session.rollback()
                    return False

    return True


def apaga_dias_marcados(plantao: Plantao | None, dias_marcados_plantao):
    if plantao:
        if plantao.data_fechamento:
            if plantao.data_fechamento < datetime.now():
                try:
                    for dia in dias_marcados_plantao:
                        dia.status = False

                    db.session.commit()
                except:
                    db.session.rollback()
                    return False

    return True


# Funcionalidades Setter
def busca_atendidos_modal():
    # atendidos = serializar()
    atendidos = (
        db.session.query(Atendido).filter(Atendido.status == 1).order_by(Atendido.nome)
    )

    return serializar(atendidos)


def busca_assistencias_judiciarias_modal():
    assistencias_judiciarias = db.session.query(AssistenciaJudiciaria)
    return serializar(assistencias_judiciarias)
