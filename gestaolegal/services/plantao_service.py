import logging
from datetime import date, datetime, time
from typing import Any, Optional

from gestaolegal.common.constants import UserRole, acoes
from gestaolegal.models.dia_plantao import DiaPlantao
from gestaolegal.models.dias_marcados_plantao import DiasMarcadosPlantao
from gestaolegal.models.fila_atendidos import FilaAtendidos
from gestaolegal.models.notificacao import Notificacao
from gestaolegal.models.plantao import Plantao
from gestaolegal.models.registro_entrada import RegistroEntrada
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.schemas.dia_plantao import DiaPlantaoSchema
from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema
from gestaolegal.schemas.fila_atendidos import FilaAtendidosSchema
from gestaolegal.schemas.notificacao import NotificacaoSchema
from gestaolegal.schemas.plantao import PlantaoSchema
from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema

logger = logging.getLogger(__name__)


class PlantaoValidator:
    @staticmethod
    def check_date_availability(
        data_marcada: date,
        user_id: int,
        user_role: str,
        dias_abertos: list[date],
        dias_usuario_marcado: list[DiasMarcadosPlantao],
    ) -> dict[str, Any]:
        if data_marcada not in dias_abertos:
            return {
                "disponivel": False,
                "mensagem": "Data selecionada não foi aberta para plantão.",
                "tipo_mensagem": "warning",
            }

        if data_marcada in [dia.data_marcada for dia in dias_usuario_marcado]:
            return {
                "disponivel": False,
                "mensagem": "Você já marcou plantão neste dia!",
                "tipo_mensagem": "warning",
            }

        return {
            "disponivel": True,
            "mensagem": "Data disponível para plantão.",
            "tipo_mensagem": "success",
        }

    @staticmethod
    def get_role_limits(user_role: UserRole) -> int:
        limits = {
            UserRole.ORIENTADOR: 1,
            UserRole.ESTAGIARIO_DIREITO: 3,
        }
        return limits.get(user_role, 0)


class PlantaoService:
    def __init__(self):
        self.plantao_repo = BaseRepository(PlantaoSchema, Plantao)
        self.dia_plantao_repo = BaseRepository(DiaPlantaoSchema, DiaPlantao)
        self.dias_marcados_repo = BaseRepository(
            DiasMarcadosPlantaoSchema, DiasMarcadosPlantao
        )
        self.registro_entrada_repo = BaseRepository(
            RegistroEntradaSchema, RegistroEntrada
        )
        self.fila_atendidos_repo = BaseRepository(FilaAtendidosSchema, FilaAtendidos)
        self.notificacao_repo = BaseRepository(NotificacaoSchema, Notificacao)
        self.validator = PlantaoValidator()

    def get_active_plantao(self) -> Plantao:
        result = self.plantao_repo.get_by_fields(
            filters={"status": True}, page_params={"page": 1, "per_page": 1}
        )

        if not result or not result.items[0]:
            raise ValueError("No active plantão found")

        return result.items[0]

    def create_plantao(
        self,
        data_abertura: Optional[datetime] = None,
        data_fechamento: Optional[datetime] = None,
    ) -> PlantaoSchema:
        return self.plantao_repo.create(
            data_abertura=data_abertura, data_fechamento=data_fechamento
        )

    def update_plantao(self, plantao_id: int, **kwargs) -> Optional[Plantao]:
        """Update plantão with provided data"""
        return self.plantao_repo.update(plantao_id, kwargs)

    def close_plantao_if_expired(self, plantao: Plantao) -> bool:
        if (
            plantao
            and plantao.data_fechamento
            and plantao.data_fechamento < datetime.now()
        ):
            self.dia_plantao_repo.delete(id=plantao.id)
            result = self.plantao_repo.get_by_fields(
                filters={"status": True}, page_params={"page": 1, "per_page": 1}
            )
            if result.items:
                active_plantao = result.items[0]
                self.plantao_repo.update(
                    active_plantao.id, data_fechamento=None, data_abertura=None
                )
            return True
        return False

    def get_user_scheduled_days(self, user_id: int) -> list[DiasMarcadosPlantao]:
        logger.info(f"Getting scheduled days for user: {user_id}")
        result = self.dias_marcados_repo.get_by_fields(
            filters={"id_usuario": user_id}, active_only=True
        )
        return [DiasMarcadosPlantao.from_sqlalchemy(dia) for dia in result.items]

    def get_available_days(self) -> list[date]:
        dias_abertos = self.dia_plantao_repo.get_all()
        return [dia.data for dia in dias_abertos]

    def schedule_day(self, data_marcada: date, user_id: int) -> bool:
        return self.dias_marcados_repo.create(
            data_marcada=data_marcada, id_usuario=user_id, status=True
        )

    def cancel_user_schedules(self, user_id: int) -> bool:
        result = self.dias_marcados_repo.get_by_fields(
            filters={"id_usuario": user_id}, active_only=True
        )
        for dia in result.items:
            self.dias_marcados_repo.soft_delete(dia.id)
        return True

    def check_date_availability(
        self, data_marcada: date, user_id: int, user_role: str
    ) -> dict[str, Any]:
        dias_abertos = self.get_available_days()
        dias_usuario_marcado = self.get_user_scheduled_days(user_id)

        return self.validator.check_date_availability(
            data_marcada, user_id, user_role, dias_abertos, dias_usuario_marcado
        )

    # ===== ATTENDANCE MANAGEMENT =====

    def get_user_attendance_status(self, user_id: int) -> dict[str, Any]:
        import pytz

        data_hora_atual = datetime.now(tz=pytz.timezone("America/Sao_Paulo"))
        status_presenca = "Entrada"

        result = self.registro_entrada_repo.get_by_fields(
            filters={"id_usuario": user_id, "status": True}
        )
        verifica_historico = result.items

        if verifica_historico:
            if (
                (data_hora_atual.day - verifica_historico[0].data_saida.day >= 1)
                or (data_hora_atual.month - verifica_historico[0].data_saida.month >= 1)
                or (data_hora_atual.year - verifica_historico[0].data_saida.year >= 1)
            ):
                self.dias_marcados_repo.update(
                    verifica_historico[0].id, {"status": False}
                )
            else:
                status_presenca = "Saída"

        return {"data_hora_atual": data_hora_atual, "status_presenca": status_presenca}

    def register_attendance(self, user_id: int, hora_registrada: str) -> dict[str, str]:
        def create_response(
            mensagem: str, tipo_mensagem: str, status: str
        ) -> dict[str, str]:
            return {
                "mensagem": mensagem,
                "tipo_mensagem": tipo_mensagem,
                "status": status,
            }

        data_atual = date.today()
        hora_registrada_split = hora_registrada.split(":")
        hora_formatada = time(
            int(hora_registrada_split[0]), int(hora_registrada_split[1])
        )
        data_hora_registrada = datetime.combine(data_atual, hora_formatada)

        result = self.registro_entrada_repo.get_by_fields(
            filters={"id_usuario": user_id, "status": True}
        )
        verifica_historico = result.items

        if verifica_historico:
            self.dias_marcados_repo.update(
                verifica_historico[0].id,
                {"data_saida": data_hora_registrada, "status": False},
            )
            return create_response(
                "Hora de saída registrada com sucesso!", "success", "Entrada"
            )
        else:
            self.registro_entrada_repo.create(
                {
                    "data_entrada": data_hora_registrada,
                    "data_saida": datetime.combine(date.today(), time(23, 59, 59)),
                    "id_usuario": user_id,
                }
            )
            return create_response(
                "Hora de entrada registrada com sucesso", "success", "Saída"
            )

    # ===== QUEUE MANAGEMENT =====

    def create_attendance_queue(self, data: dict[str, Any]) -> dict[str, str]:
        fila = self.fila_atendidos_repo.create(
            {
                "psicologia": data["psicologia"],
                "prioridade": data["prioridade"],
                "data_criacao": datetime.now(),
                "senha": data["senha"],
                "id_atendido": data["id_atendido"],
                "status": 0,
            }
        )
        return {"message": "success" if fila.id else "error"}

    def update_queue_status(self, fila_id: int, novo_status: int) -> dict[str, str]:
        fila = self.fila_atendidos_repo.find_by_id(fila_id)
        if fila:
            self.fila_atendidos_repo.update(fila_id, {"status": novo_status})
            return {"message": "Status atualizado com sucesso"}
        return {"message": "Fila não encontrada"}

    def get_today_attendance_queue(self) -> list[dict[str, Any]]:
        today = datetime.now()

        where_conditions: WhereConditions = [
            (
                "data_criacao",
                "between",
                (
                    today.strftime("%Y-%m-%d 00:00:00"),
                    today.strftime("%Y-%m-%d 23:59:59"),
                ),
            )
        ]
        result = self.fila_atendidos_repo.get(where_conditions=where_conditions)
        fila = result.items

        return [
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
            for f in fila
        ]

    # ===== REPORTING AND CONFIGURATION =====

    def get_plantao_schedule(self) -> list[dict[str, Any]]:
        datas_ja_marcadas = self.dias_marcados_repo.get_all()

        escala = []
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
        return escala

    def get_plantao_duration_days(self) -> list[date]:
        dias_duracao_gravados = self.dia_plantao_repo.get_all()
        return [dia_duracao.data for dia_duracao in dias_duracao_gravados]

    def get_monthly_availability(
        self, ano: int, mes: int, user_role: str
    ) -> list[dict[str, Any]]:
        """Get availability for a specific month."""
        dias_abertos_plantao = self.dia_plantao_repo.get_all()

        lista_dias_abertos = [
            dia_aberto.data
            for dia_aberto in dias_abertos_plantao
            if dia_aberto.data.month == mes and dia_aberto.data.year == ano
        ]

        dias = []
        for data in lista_dias_abertos:
            vagas_disponiveis = self._count_available_slots(data, user_role)
            dias.append({"Dia": str(data.day), "Vagas": vagas_disponiveis})

        return dias

    def get_available_slots_for_date(
        self, ano: int, mes: int, dia: int, user_role: str
    ) -> dict[str, int]:
        """Get available slots for a specific date."""
        data_marcada = date(ano, mes, dia)
        self.get_available_days()
        num_vagas = self._count_available_slots(data_marcada, user_role)
        return {"NumeroVagas": num_vagas}

    def _count_available_slots(self, data: date, user_role: str) -> int:
        """Count available slots for a specific date and role."""
        if data not in self.get_available_days():
            return 0

        result = self.dias_marcados_repo.get_by_fields(
            filters={"data_marcada": data, "usuario.urole": user_role}
        )
        vagas_preenchidas = result.items

        role_limit = self.validator.get_role_limits(user_role)
        if not role_limit:
            return 999

        return max(0, role_limit - len(vagas_preenchidas))

    def get_plantao_configuration(self) -> dict[str, Any]:
        hoje = datetime.now()
        result = self.plantao_repo.get_by_fields(filters={"status": True})
        dias_plantao = result.items

        dias_front = [
            (data.data.year, data.data.month, data.data.day) for data in dias_plantao
        ]

        plantao = self.get_active_plantao()
        if not plantao:
            raise ValueError("Plantao not found")
        self.close_plantao_if_expired(plantao)

        return {
            "dias_front": dias_front,
            "plantao": plantao,
            "periodo": f"{hoje.month + 1:02}/{hoje.year}",
        }

    def configure_plantao(
        self,
        datas_duracao: list[str],
        data_abertura: str,
        hora_abertura: str,
        data_fechamento: str,
        hora_fechamento: str,
        user_id: int,
    ) -> dict[str, str]:
        def create_response(mensagem: str, tipo_mensagem: str) -> dict[str, str]:
            return {"mensagem": mensagem, "tipo_mensagem": tipo_mensagem}

        plantao = self.get_active_plantao()
        status_data_abertura = False
        status_data_fechamento = False

        if datas_duracao:
            self._process_duration_dates(datas_duracao)

        if data_abertura and hora_abertura:
            status_data_abertura = self._configure_opening_date(
                data_abertura, hora_abertura, plantao, user_id
            )

        if data_fechamento and hora_fechamento:
            status_data_fechamento = self._configure_closing_date(
                data_fechamento, hora_fechamento, plantao, user_id
            )

        if status_data_abertura and status_data_fechamento:
            return create_response(
                "Data de abertura e fechamento do plantão configurada com sucesso!",
                "success",
            )
        elif status_data_abertura and not status_data_fechamento:
            return create_response(
                "Data de fechamento não pôde ser configurada!", "warning"
            )
        elif not status_data_abertura and status_data_fechamento:
            return create_response(
                "Data de abertura não pôde ser configurada!", "warning"
            )
        else:
            return create_response(
                "Não foi possível configurar as datas de abertura e fechamento!",
                "warning",
            )

    def _process_duration_dates(self, datas_duracao: list[str]) -> None:
        processed_dates = []
        for data_str in datas_duracao:
            processed_dates.append(datetime.strptime(data_str[0:10], "%d/%m/%Y").date())

        existing_dates = self.dia_plantao_repo.get_all()
        existing_date_list = [data.data for data in existing_dates]

        for data in processed_dates:
            if data not in existing_date_list:
                self.dia_plantao_repo.create({"data": data})

        for duracao in existing_dates:
            if duracao.data not in processed_dates:
                self.dia_plantao_repo.delete(duracao.id)

    def _configure_opening_date(
        self, data_abertura: str, hora_abertura: str, plantao: Plantao, user_id: int
    ) -> bool:
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
            self.create_plantao(data_abertura=data_abertura_nova)
        else:
            result = self.plantao_repo.get_by_fields(
                filters={"status": True}, page_params={"page": 1, "per_page": 1}
            )
            if result.items:
                active_plantao = result.items[0]
                self.plantao_repo.update(
                    active_plantao.id, data_abertura=data_abertura_nova
                )

        self._create_opening_notification(user_id)
        return True

    def _configure_closing_date(
        self, data_fechamento: str, hora_fechamento: str, plantao: Plantao, user_id: int
    ) -> bool:
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
            self.create_plantao(data_fechamento=data_fechamento_nova)
        else:
            result = self.plantao_repo.get_by_fields(
                filters={"status": True}, page_params={"page": 1, "per_page": 1}
            )
            if result.items:
                active_plantao = result.items[0]
                self.plantao_repo.update(
                    active_plantao.id, data_fechamento=data_fechamento_nova
                )

        return True

    def _create_opening_notification(self, user_id: int) -> None:
        notificacao_data = {
            "acao": acoes["ABERTURA_PLANTAO"],
            "data": datetime.now(),
            "id_executor_acao": user_id,
        }
        self.notificacao_repo.create(notificacao_data)

    def get_numero_plantao_a_marcar(self, id_usuario: int) -> int:
        """Get the next plantao number for a user."""
        result = self.dias_marcados_repo.get_by_fields(
            filters={"id_usuario": id_usuario}, active_only=True
        )
        return len(result.items) + 1

    def get_plantao_page_data(self, user_id: int, user_role: str) -> dict[str, Any]:
        """Get all data needed for the plantão page"""
        self.get_user_scheduled_days(user_id)
        plantao = self.get_active_plantao()

        if plantao:
            self.apagar_dias_marcados_usuario(plantao.id)

        # Check access permissions
        if user_role not in [UserRole.ADMINISTRADOR, UserRole.COLAB_PROJETO] and (
            plantao and plantao.data_abertura is None
        ):
            return {
                "access_granted": False,
                "message": "O plantão não está aberto!",
                "dias_usuario_atual": [],
                "numero_plantao": 0,
            }

        dias_usuario_atual = self.get_user_scheduled_days(user_id)
        numero_plantao = self.get_numero_plantao_a_marcar(user_id)

        return {
            "access_granted": True,
            "message": "",
            "dias_usuario_atual": dias_usuario_atual,
            "numero_plantao": numero_plantao,
        }

    def check_plantao_access(self, user_role: str) -> bool:
        """Check if user has access to plantão functionality"""
        plantao = self.get_active_plantao()
        # valida_fim_plantao method doesn't exist, removing call

        if user_role not in [UserRole.ADMINISTRADOR, UserRole.COLAB_PROJETO] and (
            plantao and plantao.data_abertura is None
        ):
            return False
        return True

    def confirmar_data_plantao(
        self, data_marcada: date, user_id: int, user_role: str, data_atual: date
    ) -> dict[str, Any]:
        """Handle plantão date confirmation with all business logic"""
        from flask import render_template

        def cria_json(lista_datas, mensagem, tipo_mensagem: str):
            return {
                "lista_datas": lista_datas,
                "mensagem": mensagem,
                "tipo_mensagem": tipo_mensagem,
                "numero_plantao": self.get_numero_plantao_a_marcar(user_id),
            }

        dias_usuario_marcado = self.get_user_scheduled_days(user_id)

        disponibilidade = self.check_date_availability(data_marcada, user_id, user_role)

        if not disponibilidade["disponivel"]:
            return cria_json(
                render_template(
                    "plantao/componentes/lista_datas_plantao.html",
                    data_atual=data_atual,
                    datas_plantao=dias_usuario_marcado,
                ),
                disponibilidade["mensagem"],
                disponibilidade["tipo_mensagem"],
            )

        # Check user limits
        if len(dias_usuario_marcado) >= 2 or (
            len(dias_usuario_marcado) >= 1 and user_role == UserRole.ORIENTADOR
        ):
            return cria_json(
                render_template(
                    "plantao/componentes/lista_datas_plantao.html",
                    datas_plantao=dias_usuario_marcado,
                    data_atual=data_atual,
                ),
                "Você atingiu o limite de plantões cadastrados.",
                "warning",
            )

        # Try to schedule the day
        if self.confirmar_data_plantao(data_marcada, user_id, user_role, data_atual):
            mensagem = "Data de plantão cadastrada!"
            tipo_mensagem = "success"
        else:
            mensagem = "Erro ao cadastrar data de plantão."
            tipo_mensagem = "error"

        dias_usuario_atual = self.get_user_scheduled_days(user_id)
        return cria_json(
            render_template(
                "plantao/componentes/lista_datas_plantao.html",
                datas_plantao=dias_usuario_atual,
                data_atual=data_atual,
            ),
            mensagem,
            tipo_mensagem,
        )

    def apagar_dias_marcados_usuario(self, user_id: int) -> tuple[bool, str]:
        """Delete user's scheduled days and return success status and message"""
        try:
            success = self.cancel_user_schedules(user_id)
            if success:
                return (
                    True,
                    "Registro apagado. Por favor, selecione novamente os dias para o seu plantão",
                )
            else:
                return False, "Erro ao apagar registros"
        except Exception as e:
            logger.error(f"Error deleting user schedules: {str(e)}")
            return False, "Erro ao apagar registros"

    def populate_forms(self, form_abrir, form_fechar, plantao):
        """Populate forms with plantão data"""
        if plantao:
            if plantao.data_abertura:
                form_abrir.data_abertura.data = plantao.data_abertura.date()
                form_abrir.hora_abertura.data = plantao.data_abertura.time()
            if plantao.data_fechamento:
                form_fechar.data_fechamento.data = plantao.data_fechamento.date()
                form_fechar.hora_fechamento.data = plantao.data_fechamento.time()
