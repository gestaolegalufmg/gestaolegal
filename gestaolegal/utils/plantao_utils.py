from datetime import date, datetime

from flask import flash, redirect, url_for
from flask_login import current_user

from gestaolegal.common.constants import UserRole, assistencia_jud_areas_atendidas
from gestaolegal.database import get_db
from gestaolegal.forms.plantao import AbrirPlantaoForm, FecharPlantaoForm
from gestaolegal.schemas.assistencia_judiciaria import AssistenciaJudiciariaSchema
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.dia_plantao import DiaPlantaoSchema
from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema
from gestaolegal.schemas.plantao import PlantaoSchema
from gestaolegal.schemas.usuario import UsuarioSchema

filtro_busca_assistencia_judiciaria = assistencia_jud_areas_atendidas
filtro_busca_assistencia_judiciaria["TODAS"] = ("todas", "Todas")


def validaDadosEditar_atendidoForm(form, emailAtual: str):
    db = get_db()

    emailRepetido = (
        db.session.query(AtendidoSchema).filter_by(email=form.email.data).first()
    )

    if not form.validate():
        return False
    if (emailRepetido) and (form.email.data != emailAtual):
        flash("Este email já está em uso.", "warning")
        return False
    return True


def serializar(lista):
    return [x.as_dict() for x in lista]


def numero_plantao_a_marcar(id_usuario: int):
    db = get_db()

    dias_marcados = (
        db.session.query(DiasMarcadosPlantaoSchema)
        .filter_by(id_usuario=id_usuario)
        .all()
    )
    return len(dias_marcados) + 1


def checa_vagas_em_todos_dias(dias_disponiveis: list, urole: str) -> bool:
    """
    Função que retorna verdadeiro caso NÃO exista vagas para um determinado tipo de usuario
    """
    db = get_db()

    if urole == UserRole.ORIENTADOR:
        orientador_no_dia = []  # essa lista armazena se todos os dias tem ou nao um orientador ja cadastrado num dia, true caso sim e false do contrario
        for i in range(0, len(dias_disponiveis)):
            seletor_banco_de_dados = (
                db.session.query(DiasMarcadosPlantaoSchema)
                .filter_by(data_marcada=dias_disponiveis[i])
                .all()
            )
            for data in seletor_banco_de_dados:
                if data.usuario.urole == UserRole.ORIENTADOR:
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
                db.session.query(DiasMarcadosPlantaoSchema)
                .filter_by(data_marcada=dias_disponiveis[i])
                .all()
            )
            numero_de_estagiarios_no_dia = 0
            for data in seletor_banco_de_dados:
                if data.usuario.urole == UserRole.ESTAGIARIO_DIREITO:
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
    db = get_db()

    urole_usuario = current_user.urole
    consulta_data_marcada = (
        db.session.query(DiasMarcadosPlantaoSchema).filter_by(data_marcada=data).all()
    )
    numero_orientador = 0
    numero_estagiario = 0

    for data in consulta_data_marcada:
        if data.usuario.urole == UserRole.ORIENTADOR:
            numero_orientador += 1
        else:
            numero_estagiario += 1

    if (urole_usuario == UserRole.ORIENTADOR) and (numero_orientador >= 1):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False

    elif (urole_usuario == UserRole.ESTAGIARIO_DIREITO) and (numero_estagiario >= 3):
        if checa_vagas_em_todos_dias(dias_disponiveis, urole_usuario):
            return True
        return False
    else:
        return True


def resposta_configura_abertura() -> redirect:
    return redirect(url_for("plantao.pg_plantao"))


def atualiza_data_abertura(form: AbrirPlantaoForm, plantao: PlantaoSchema):
    db = get_db()

    data_escolhida = form.data_abertura.data
    hora_escolhida = form.hora_abertura.data

    plantao.data_abertura = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()


def atualiza_data_fechamento(form: FecharPlantaoForm, plantao: PlantaoSchema):
    db = get_db()

    data_escolhida = form.data_fechamento.data
    hora_escolhida = form.hora_fechamento.data

    plantao.data_fechamento = datetime.combine(data_escolhida, hora_escolhida)
    db.session.commit()


def set_abrir_plantao_form(form: AbrirPlantaoForm, plantao: PlantaoSchema):
    if plantao:
        if plantao.data_abertura:
            form.data_abertura.data = plantao.data_abertura.date()
            form.hora_abertura.data = plantao.data_abertura.time()


def set_fechar_plantao_form(form: FecharPlantaoForm, plantao: PlantaoSchema):
    if plantao:
        if plantao.data_fechamento:
            form.data_fechamento.data = plantao.data_fechamento.date()
            form.hora_fechamento.data = plantao.data_fechamento.time()


def vagas_restantes(dias_disponiveis: list, data: date):
    db = get_db()

    num_max = 0
    if data not in dias_disponiveis:
        return 0
    for i in range(0, len(dias_disponiveis)):
        vagas_preenchidas = (
            db.session.query(DiasMarcadosPlantaoSchema, UsuarioSchema.urole)
            .select_from(DiasMarcadosPlantaoSchema)
            .join(UsuarioSchema)
            .filter(
                UsuarioSchema.urole == current_user.urole,
                DiasMarcadosPlantaoSchema.data_marcada == dias_disponiveis[i],
            )
            .all()
        )
        if len(vagas_preenchidas) > num_max:
            num_max = len(vagas_preenchidas)
        if current_user.urole == UserRole.ORIENTADOR:
            if num_max < 1:
                num_max = 1
        if current_user.urole == UserRole.ESTAGIARIO_DIREITO:
            if num_max < 3:
                num_max = 3
    vagas_no_dia = (
        db.session.query(DiasMarcadosPlantaoSchema, UsuarioSchema.urole)
        .select_from(DiasMarcadosPlantaoSchema)
        .join(UsuarioSchema)
        .filter(
            UsuarioSchema.urole == current_user.urole,
            DiasMarcadosPlantaoSchema.data_marcada == data,
        )
        .all()
    )
    if current_user.urole not in [
        UserRole.ORIENTADOR,
        UserRole.ESTAGIARIO_DIREITO,
    ]:
        return "Sem limites"
    else:
        return num_max - len(vagas_no_dia)


def valida_fim_plantao(plantao: PlantaoSchema):
    db = get_db()

    if plantao:
        if plantao.data_fechamento:
            if plantao.data_fechamento < datetime.now():
                try:
                    db.session.query(DiaPlantaoSchema).delete()
                    db.session.flush()

                    plantao.data_fechamento = None
                    plantao.data_abertura = None
                    db.session.commit()
                except:
                    db.session.rollback()
                    return False

    return True


def apaga_dias_marcados(plantao: PlantaoSchema | None, dias_marcados_plantao):
    db = get_db()

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
    db = get_db()

    # atendidos = serializar()
    atendidos = (
        db.session.query(AtendidoSchema)
        .filter(AtendidoSchema.status == 1)
        .order_by(AtendidoSchema.nome)
    )

    return serializar(atendidos)


def busca_assistencias_judiciarias_modal():
    db = get_db()

    assistencias_judiciarias = db.session.query(AssistenciaJudiciariaSchema)
    return serializar(assistencias_judiciarias)
