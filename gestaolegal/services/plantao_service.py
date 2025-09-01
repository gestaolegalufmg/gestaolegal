from datetime import date, datetime, time, timedelta
from typing import List, Optional, TypeVar

from sqlalchemy.orm import Query

from gestaolegal.common.constants import UserRole
from gestaolegal.models.dias_marcados_plantao import DiasMarcadosPlantao
from gestaolegal.models.plantao import Plantao
from gestaolegal.schemas.dia_plantao import DiaPlantaoSchema
from gestaolegal.schemas.dias_marcados_plantao import DiasMarcadosPlantaoSchema
from gestaolegal.schemas.fila_atendidos import FilaAtendidosSchema
from gestaolegal.schemas.plantao import PlantaoSchema
from gestaolegal.schemas.registro_entrada import RegistroEntradaSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.services.base_service import BaseService

T = TypeVar("T")


class PlantaoService(BaseService[PlantaoSchema, Plantao]):
    def __init__(self):
        super().__init__(PlantaoSchema)

    def _get_plantao_by_id(self, plantao_id: int) -> Optional[PlantaoSchema]:
        return self.session.query(PlantaoSchema).get(plantao_id)

    def _get_active_plantao(self) -> Optional[PlantaoSchema]:
        return self.session.query(PlantaoSchema).first()

    def _create_plantao(
        self,
        data_abertura: Optional[datetime] = None,
        data_fechamento: Optional[datetime] = None,
    ) -> PlantaoSchema:
        plantao = PlantaoSchema(
            data_abertura=data_abertura, data_fechamento=data_fechamento
        )
        self.session.add(plantao)
        self.session.commit()
        return plantao

    def _update_plantao(self, plantao: PlantaoSchema, **kwargs) -> bool:
        try:
            for key, value in kwargs.items():
                setattr(plantao, key, value)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def _delete_plantao(self, plantao_id: int) -> bool:
        try:
            plantao = self._get_plantao_by_id(plantao_id)
            if plantao:
                self.session.delete(plantao)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            return False

    def _get_dias_marcados_by_user(
        self, user_id: int, active_only: bool = True
    ) -> List[DiasMarcadosPlantaoSchema]:
        query = self.session.query(DiasMarcadosPlantaoSchema).filter_by(
            id_usuario=user_id
        )
        if active_only:
            query = query.filter_by(status=True)
        return query.all()

    def _get_dias_marcados_by_date(
        self, data_marcada: date
    ) -> List[DiasMarcadosPlantaoSchema]:
        return (
            self.session.query(DiasMarcadosPlantaoSchema)
            .filter_by(data_marcada=data_marcada)
            .all()
        )

    def _create_dia_marcado(
        self, data_marcada: date, user_id: int
    ) -> DiasMarcadosPlantaoSchema:
        dia_marcado = DiasMarcadosPlantaoSchema(
            data_marcada=data_marcada, id_usuario=user_id, status=True
        )
        self.session.add(dia_marcado)
        self.session.commit()
        return dia_marcado

    def _update_dia_marcado(
        self, dia_marcado: DiasMarcadosPlantaoSchema, **kwargs
    ) -> bool:
        try:
            for key, value in kwargs.items():
                setattr(dia_marcado, key, value)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def _deactivate_dias_marcados_by_user(self, user_id: int) -> bool:
        try:
            dias_marcados = self._get_dias_marcados_by_user(user_id, active_only=True)
            for dia in dias_marcados:
                dia.status = False
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def _get_dias_plantao_ativos(self) -> List[DiaPlantaoSchema]:
        return self.session.query(DiaPlantaoSchema).filter_by(status=True).all()

    def _create_dia_plantao(self, data: date) -> DiaPlantaoSchema:
        dia_plantao = DiaPlantaoSchema(data=data)
        self.session.add(dia_plantao)
        self.session.commit()
        return dia_plantao

    def _delete_dia_plantao(self, dia_id: int) -> bool:
        try:
            self.session.query(DiaPlantaoSchema).filter(
                DiaPlantaoSchema.id == dia_id
            ).delete()
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def _get_registro_entrada_ativo(
        self, user_id: int
    ) -> Optional[RegistroEntradaSchema]:
        return (
            self.session.query(RegistroEntradaSchema)
            .filter(
                RegistroEntradaSchema.id_usuario == user_id,
                RegistroEntradaSchema.status == True,
            )
            .first()
        )

    def _create_registro_entrada(
        self, user_id: int, data_entrada: datetime, data_saida: datetime
    ) -> RegistroEntradaSchema:
        registro = RegistroEntradaSchema(
            data_entrada=data_entrada, data_saida=data_saida, id_usuario=user_id
        )
        self.session.add(registro)
        self.session.commit()
        return registro

    def _get_fila_by_id(self, fila_id: int) -> Optional[FilaAtendidosSchema]:
        return self.session.query(FilaAtendidosSchema).get(fila_id)

    def _create_fila_atendimento(self, **kwargs) -> FilaAtendidosSchema:
        fila = FilaAtendidosSchema(**kwargs)
        self.session.add(fila)
        self.session.commit()
        return fila

    def _update_fila_status(self, fila_id: int, novo_status: int) -> bool:
        try:
            fila = self._get_fila_by_id(fila_id)
            if fila:
                fila.status = novo_status
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            return False

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(PlantaoSchema.status == True)

    def get_plantao_ativo(self) -> Plantao | None:
        plantao_schema = self._get_active_plantao()
        return Plantao.from_sqlalchemy(plantao_schema) if plantao_schema else None

    def get_dias_usuario_marcado(self, user_id: int) -> list[DiasMarcadosPlantao]:
        dias_marcados = self._get_dias_marcados_by_user(user_id, active_only=True)
        return [DiasMarcadosPlantao.from_sqlalchemy(dia) for dia in dias_marcados]

    def get_dias_abertos_plantao(self) -> list[date]:
        dias_abertos = self._get_dias_plantao_ativos()
        return [dia.data for dia in dias_abertos]

    def get_escala_plantao(self) -> list[dict]:
        datas_ja_marcadas = (
            self.session.query(DiasMarcadosPlantaoSchema)
            .filter(DiasMarcadosPlantaoSchema.status == True)
            .all()
        )

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

    def get_duracao_plantao(self) -> list[date]:
        dias_duracao_gravados = self._get_dias_plantao_ativos()
        return [dia_duracao.data for dia_duracao in dias_duracao_gravados]

    def verificar_disponibilidade_data(
        self, data_marcada: date, user_id: int, user_role: str
    ) -> dict:
        dias_abertos = self.get_dias_abertos_plantao()
        dias_usuario_marcado = self.get_dias_usuario_marcado(user_id)

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

        if not self._confirma_disponibilidade_dia(
            dias_abertos, data_marcada, user_role
        ):
            return {
                "disponivel": False,
                "mensagem": "Não há vagas disponíveis na data selecionada, tente outro dia.",
                "tipo_mensagem": "warning",
            }

        return {
            "disponivel": True,
            "mensagem": "Data disponível para plantão.",
            "tipo_mensagem": "success",
        }

    def marcar_data_plantao(self, data_marcada: date, user_id: int) -> bool:
        try:
            self._create_dia_marcado(data_marcada, user_id)
            return True
        except Exception:
            self.session.rollback()
            return False

    def apagar_dias_marcados_usuario(self, user_id: int) -> bool:
        return self._deactivate_dias_marcados_by_user(user_id)

    def get_disponibilidade_vagas_mes(
        self, ano: int, mes: int, user_role: str
    ) -> list[dict]:
        dias_abertos_plantao = self._get_dias_plantao_ativos()

        lista_dias_abertos = [
            dia_aberto.data
            for dia_aberto in dias_abertos_plantao
            if dia_aberto.data.month == mes and dia_aberto.data.year == ano
        ]

        dias = []
        for data in lista_dias_abertos:
            disponivel = self._confirma_disponibilidade_dia(
                lista_dias_abertos, data, user_role
            )
            dias.append({"Dia": str(data.day), "Vagas": disponivel})

        return dias

    def get_vagas_disponiveis_data(
        self, ano: int, mes: int, dia: int, user_role: str
    ) -> dict:
        data_marcada = date(ano, mes, dia)
        dias_abertos = self.get_dias_abertos_plantao()
        num_vagas = self._vagas_restantes(dias_abertos, data_marcada, user_role)
        return {"NumeroVagas": num_vagas}

    def _confirma_disponibilidade_dia(
        self, dias_disponiveis: list, data: date, user_role: str
    ) -> bool:
        consulta_data_marcada = self._get_dias_marcados_by_date(data)
        numero_orientador = 0
        numero_estagiario = 0

        for data_marcada in consulta_data_marcada:
            if data_marcada.usuario.urole == UserRole.ORIENTADOR:
                numero_orientador += 1
            else:
                numero_estagiario += 1

        if (user_role == UserRole.ORIENTADOR) and (numero_orientador >= 1):
            if self._checa_vagas_em_todos_dias(dias_disponiveis, user_role):
                return True
            return False
        elif (user_role == UserRole.ESTAGIARIO_DIREITO) and (numero_estagiario >= 3):
            if self._checa_vagas_em_todos_dias(dias_disponiveis, user_role):
                return True
            return False
        else:
            return True

    def _checa_vagas_em_todos_dias(
        self, dias_disponiveis: list, user_role: str
    ) -> bool:
        if user_role == UserRole.ORIENTADOR:
            orientador_no_dia = []
            for dia_disponivel in dias_disponiveis:
                seletor_banco_de_dados = self._get_dias_marcados_by_date(dia_disponivel)
                for data in seletor_banco_de_dados:
                    if data.usuario.urole == UserRole.ORIENTADOR:
                        orientador_no_dia.append(True)
                        break

            if len(orientador_no_dia) < len(dias_disponiveis):
                return False
            else:
                return True
        else:
            tres_estagiarios_no_dia = []
            for dia_disponivel in dias_disponiveis:
                seletor_banco_de_dados = self._get_dias_marcados_by_date(dia_disponivel)
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

    def _vagas_restantes(
        self, dias_disponiveis: list, data: date, user_role: str
    ) -> int | str:
        num_max = 0
        if data not in dias_disponiveis:
            return 0

        for dia_disponivel in dias_disponiveis:
            vagas_preenchidas = (
                self.session.query(DiasMarcadosPlantaoSchema, UsuarioSchema.urole)
                .select_from(DiasMarcadosPlantaoSchema)
                .join(UsuarioSchema)
                .filter(
                    UsuarioSchema.urole == user_role,
                    DiasMarcadosPlantaoSchema.data_marcada == dia_disponivel,
                )
                .all()
            )
            if len(vagas_preenchidas) > num_max:
                num_max = len(vagas_preenchidas)

        if user_role == UserRole.ORIENTADOR:
            if num_max < 1:
                num_max = 1
        if user_role == UserRole.ESTAGIARIO_DIREITO:
            if num_max < 3:
                num_max = 3

        vagas_no_dia = (
            self.session.query(DiasMarcadosPlantaoSchema, UsuarioSchema.urole)
            .select_from(DiasMarcadosPlantaoSchema)
            .join(UsuarioSchema)
            .filter(
                UsuarioSchema.urole == user_role,
                DiasMarcadosPlantaoSchema.data_marcada == data,
            )
            .all()
        )

        if user_role not in [UserRole.ORIENTADOR, UserRole.ESTAGIARIO_DIREITO]:
            return "Sem limites"
        else:
            return num_max - len(vagas_no_dia)

    def valida_fim_plantao(self, plantao: Plantao) -> bool:
        if (
            plantao
            and plantao.data_fechamento
            and plantao.data_fechamento < datetime.now()
        ):
            try:
                self.session.query(DiaPlantaoSchema).delete()
                self.session.flush()

                plantao_schema = self._get_active_plantao()
                if plantao_schema:
                    self._update_plantao(
                        plantao_schema, data_fechamento=None, data_abertura=None
                    )
                return True
            except Exception:
                self.session.rollback()
                return False
        return True

    def apaga_dias_marcados(
        self, plantao: Plantao | None, dias_marcados_plantao: list
    ) -> bool:
        if (
            plantao
            and plantao.data_fechamento
            and plantao.data_fechamento < datetime.now()
        ):
            try:
                for dia in dias_marcados_plantao:
                    dia_schema = self.session.query(DiasMarcadosPlantaoSchema).get(
                        dia.id
                    )
                    if dia_schema:
                        self._update_dia_marcado(dia_schema, status=False)
                return True
            except Exception:
                self.session.rollback()
                return False
        return True

    def get_status_presenca_usuario(self, user_id: int) -> dict:
        import pytz

        data_hora_atual = datetime.now(tz=pytz.timezone("America/Sao_Paulo"))
        status_presenca = "Entrada"

        verifica_historico = self._get_registro_entrada_ativo(user_id)

        if verifica_historico:
            if (
                (data_hora_atual.day - verifica_historico.data_saida.day >= 1)
                or (data_hora_atual.month - verifica_historico.data_saida.month >= 1)
                or (data_hora_atual.year - verifica_historico.data_saida.year >= 1)
            ):
                self._update_dia_marcado(verifica_historico, status=False)
            else:
                status_presenca = "Saída"

        return {"data_hora_atual": data_hora_atual, "status_presenca": status_presenca}

    def registrar_presenca(self, user_id: int, hora_registrada: str) -> dict:
        def cria_json(mensagem: str, tipo_mensagem: str, status: str) -> dict:
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

        verifica_historico = self._get_registro_entrada_ativo(user_id)

        if verifica_historico:
            self._update_dia_marcado(
                verifica_historico, data_saida=data_hora_registrada, status=False
            )
            return cria_json(
                "Hora de saída registrada com sucesso!", "success", "Entrada"
            )
        else:
            self._create_registro_entrada(
                user_id=user_id,
                data_entrada=data_hora_registrada,
                data_saida=datetime.combine(date.today(), time(23, 59, 59)),
            )
            return cria_json(
                "Hora de entrada registrada com sucesso", "success", "Saída"
            )

    def confirmar_presencas(self, dados_confirmacao: dict) -> bool:
        try:
            for chave, valor in dados_confirmacao.items():
                if chave == "csrf_token":
                    continue

                tipo_confirmacao = chave.split("_")

                if tipo_confirmacao[0] == "plantao":
                    plantao = self.session.query(DiasMarcadosPlantaoSchema).get_or_404(
                        int(tipo_confirmacao[1])
                    )
                    self._update_dia_marcado(plantao, confirmacao=valor)
                else:
                    presenca = self.session.query(RegistroEntradaSchema).get_or_404(
                        int(tipo_confirmacao[1])
                    )
                    self._update_dia_marcado(presenca, confirmacao=valor)

            return True
        except Exception:
            self.session.rollback()
            return False

    def get_presencas_para_confirmacao(self) -> dict:
        if date.today().weekday() != 1:
            data_ontem = date.today() - timedelta(days=1)
        else:
            data_ontem = date.today() - timedelta(days=3)

        presencas_registradas = (
            self.session.query(RegistroEntradaSchema)
            .filter(
                RegistroEntradaSchema.status == False,
                RegistroEntradaSchema.confirmacao == "aberto",
            )
            .all()
        )

        presencas_ontem = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_ontem
        ]

        plantoes_ontem = (
            self.session.query(DiasMarcadosPlantaoSchema)
            .filter(
                DiasMarcadosPlantaoSchema.data_marcada == data_ontem,
                DiasMarcadosPlantaoSchema.confirmacao == "aberto",
            )
            .all()
        )

        return {
            "presencas_registradas": presencas_ontem,
            "plantoes_registradas": plantoes_ontem,
            "data_ontem": data_ontem,
        }

    def buscar_presencas_por_data(self, data_procurada_string: str) -> dict:
        def cria_json(
            presencas: list, plantoes: list, tem_presenca: bool, tem_plantao: bool
        ) -> dict:
            return {
                "presencas": presencas,
                "plantoes": plantoes,
                "tem_presenca": tem_presenca,
                "tem_plantao": tem_plantao,
            }

        data_procurada_separada = data_procurada_string.split("-")
        data_procurada = date(
            int(data_procurada_separada[0]),
            int(data_procurada_separada[1]),
            int(data_procurada_separada[2]),
        )

        presencas_registradas = (
            self.session.query(RegistroEntradaSchema)
            .filter(
                RegistroEntradaSchema.status == False,
                RegistroEntradaSchema.confirmacao == "aberto",
            )
            .all()
        )

        presencas = [
            presenca
            for presenca in presencas_registradas
            if presenca.data_entrada.date() == data_procurada
        ]

        plantoes_marcados = (
            self.session.query(DiasMarcadosPlantaoSchema)
            .filter(
                DiasMarcadosPlantaoSchema.data_marcada == data_procurada,
                DiasMarcadosPlantaoSchema.confirmacao == "aberto",
            )
            .all()
        )

        presencas_ajax = [
            {
                "IdPresenca": presenca.id,
                "Nome": presenca.usuario.nome,
                "Cargo": UserRole.get_display_name(presenca.usuario.urole),
                "Entrada": presenca.data_entrada.strftime("%H:%M"),
                "Saida": presenca.data_saida.strftime("%H:%M"),
            }
            for presenca in presencas
        ]

        plantoes_ajax = [
            {
                "IdPlantao": plantao.id,
                "Nome": plantao.usuario.nome,
                "Cargo": UserRole.get_display_name(plantao.usuario.urole),
            }
            for plantao in plantoes_marcados
        ]

        tem_presenca = len(presencas) > 0
        tem_plantao = len(plantoes_marcados) > 0

        return cria_json(presencas_ajax, plantoes_ajax, tem_presenca, tem_plantao)

    def get_configuracao_abertura_data(self) -> dict:
        hoje = datetime.now()

        dias_plantao = (
            self.session.query(DiaPlantaoSchema.data)
            .filter(DiaPlantaoSchema.status == True)
            .all()
        )

        dias_front = [
            (data.data.year, data.data.month, data.data.day) for data in dias_plantao
        ]

        plantao = self.get_plantao_ativo()
        self.valida_fim_plantao(plantao)

        return {
            "dias_front": dias_front,
            "plantao": plantao,
            "periodo": f"{hoje.month + 1:02}/{hoje.year}",
        }

    def salvar_configuracao_plantao(
        self,
        datas_duracao: list,
        data_abertura: str,
        hora_abertura: str,
        data_fechamento: str,
        hora_fechamento: str,
        user_id: int,
    ) -> dict:
        def cria_json(mensagem: str, tipo_mensagem: str) -> dict:
            return {
                "mensagem": mensagem,
                "tipo_mensagem": tipo_mensagem,
            }

        plantao = self.get_plantao_ativo()
        status_data_abertura = False
        status_data_fechamento = False

        if datas_duracao:
            self._processar_datas_duracao(datas_duracao)

        if data_abertura and hora_abertura:
            status_data_abertura = self._configurar_data_abertura(
                data_abertura, hora_abertura, plantao, user_id
            )

        if data_fechamento and hora_fechamento:
            status_data_fechamento = self._configurar_data_fechamento(
                data_fechamento, hora_fechamento, plantao, user_id
            )

        if status_data_abertura and status_data_fechamento:
            return cria_json(
                "Data de abertura e fechamento do plantão configurada com sucesso!",
                "success",
            )
        elif status_data_abertura and not status_data_fechamento:
            return cria_json("Data de fechamento não pôde ser configurada!", "warning")
        elif not status_data_abertura and status_data_fechamento:
            return cria_json("Data de abertura não pôde ser configurada!", "warning")
        else:
            return cria_json(
                "Não foi possível configurar as datas de abertura e fechamento!",
                "warning",
            )

    def _processar_datas_duracao(self, datas_duracao: list) -> None:
        for i in range(len(datas_duracao)):
            datas_duracao[i] = datetime.strptime(
                datas_duracao[i][0:10], "%d/%m/%Y"
            ).date()

        lista_duracao_banco_dados = self.session.query(
            DiaPlantaoSchema.data, DiaPlantaoSchema.id
        ).all()
        datas_duracao_banco_dados = [data[0] for data in lista_duracao_banco_dados]

        for data in datas_duracao:
            if data not in datas_duracao_banco_dados:
                self._create_dia_plantao(data)

        for duracao in lista_duracao_banco_dados:
            if duracao[0] not in datas_duracao:
                self._delete_dia_plantao(duracao[1])

    def _configurar_data_abertura(
        self, data_abertura: str, hora_abertura: str, plantao: Plantao, user_id: int
    ) -> bool:
        try:
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
                self._create_plantao(data_abertura=data_abertura_nova)
            else:
                plantao_schema = self._get_active_plantao()
                if plantao_schema:
                    self._update_plantao(
                        plantao_schema, data_abertura=data_abertura_nova
                    )

            self._criar_notificacao_abertura(user_id)
            return True
        except Exception:
            self.session.rollback()
            return False

    def _configurar_data_fechamento(
        self, data_fechamento: str, hora_fechamento: str, plantao: Plantao, user_id: int
    ) -> bool:
        try:
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
                self._create_plantao(data_fechamento=data_fechamento_nova)
            else:
                plantao_schema = self._get_active_plantao()
                if plantao_schema:
                    self._update_plantao(
                        plantao_schema, data_fechamento=data_fechamento_nova
                    )

            return True
        except Exception:
            self.session.rollback()
            return False

    def _criar_notificacao_abertura(self, user_id: int) -> None:
        from gestaolegal.common.constants import acoes
        from gestaolegal.models.notificacao import Notificacao

        _notificacao = Notificacao(
            acao=acoes["ABERTURA_PLANTAO"],
            data=datetime.now(),
            id_executor_acao=user_id,
        )
        self.session.add(_notificacao)
        self.session.commit()

    def criar_fila_atendimento(self, data: dict) -> dict:
        try:
            fila = self._create_fila_atendimento(
                psicologia=data["psicologia"],
                prioridade=data["prioridade"],
                data_criacao=datetime.now(),
                senha=data["senha"],
                id_atendido=data["id_atendido"],
                status=0,
            )
            return {"message": "success" if fila.id else "error"}
        except Exception:
            self.session.rollback()
            return {"message": "error"}

    def atualizar_status_fila(self, fila_id: int, novo_status: int) -> dict:
        if self._update_fila_status(fila_id, novo_status):
            return {"message": "Status atualizado com sucesso"}
        else:
            return {"message": "Fila não encontrada"}

    def get_atendimentos_hoje(self) -> list:
        today = datetime.now()
        fila = (
            self.session.query(FilaAtendidosSchema)
            .filter(
                FilaAtendidosSchema.data_criacao.between(
                    today.strftime("%Y-%m-%d 00:00:00"),
                    today.strftime("%Y-%m-%d 23:59:59"),
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

        return fila_obj
