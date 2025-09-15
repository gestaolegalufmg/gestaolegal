from typing import Optional

from sqlalchemy import func, or_

from gestaolegal.models.orientacao_juridica import OrientacaoJuridica
from gestaolegal.repositories.base_repository import BaseRepository, PageParams
from gestaolegal.schemas.assistencia_judiciaria_x_orientacao_juridica import (
    AssistenciaJudiciaria_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.atendido import AtendidoSchema
from gestaolegal.schemas.atendido_x_orientacao_juridica import (
    Atendido_xOrientacaoJuridicaSchema,
)
from gestaolegal.schemas.orientacao_juridica import OrientacaoJuridicaSchema
from gestaolegal.schemas.usuario import UsuarioSchema


class OrientacaoJuridicaRepository(BaseRepository):
    def __init__(self):
        super().__init__(OrientacaoJuridicaSchema, OrientacaoJuridica)

    def get_orientacoes_count_by_area(
        self, data_inicio: str, data_fim: str, areas: Optional[list[str]] = None
    ) -> list[tuple]:
        query = self.session.query(
            OrientacaoJuridicaSchema.area_direito,
            func.count(OrientacaoJuridicaSchema.area_direito),
        ).filter(
            OrientacaoJuridicaSchema.status,
            OrientacaoJuridicaSchema.data_criacao >= data_inicio,
            OrientacaoJuridicaSchema.data_criacao <= data_fim,
        )

        if areas:
            query = query.filter(OrientacaoJuridicaSchema.area_direito.in_(areas))

        return query.group_by(OrientacaoJuridicaSchema.area_direito).all()

    def get_all_with_pagination(self, page_params: PageParams | None = None):
        return self.get(
            order_by=["data_criacao"],
            order_desc=True,
            page_params=page_params,
        )

    def get_perfil_data(self, orientacao_id: int):
        orientacao = self.find_by_id(orientacao_id)
        if not orientacao:
            return None

        atendidos_envolvidos = (
            self.session.query(AtendidoSchema)
            .join(Atendido_xOrientacaoJuridicaSchema)
            .filter(
                Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica
                == orientacao.id,
                AtendidoSchema.status,
            )
            .order_by(AtendidoSchema.nome)
            .all()
        )

        usuario = None
        if orientacao.id_usuario:
            usuario = (
                self.session.query(UsuarioSchema)
                .filter_by(id=orientacao.id_usuario)
                .first()
            )

        assistencias_envolvidas = (
            self.session.query(AssistenciaJudiciaria_xOrientacaoJuridicaSchema)
            .filter_by(id_orientacaoJuridica=orientacao.id)
            .all()
        )

        return {
            "orientacao": orientacao,
            "atendidos": atendidos_envolvidos,
            "assistencias": assistencias_envolvidas,
            "usuario": usuario or {"nome": "--"},
        }

    def buscar_atendidos(
        self, termo: str, orientacao_id: str | None = None
    ) -> list[AtendidoSchema]:
        from sqlalchemy import or_

        query = self.session.query(AtendidoSchema).filter(AtendidoSchema.status)

        if orientacao_id and orientacao_id != "0":
            query = query.outerjoin(Atendido_xOrientacaoJuridicaSchema).filter(
                (
                    Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica
                    != int(orientacao_id)
                )
                | (Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica.is_(None))
            )

        if termo:
            query = query.filter(
                or_(
                    AtendidoSchema.nome.ilike(f"%{termo}%"),
                    AtendidoSchema.cpf.ilike(f"%{termo}%"),
                    AtendidoSchema.cnpj.ilike(f"%{termo}%"),
                )
            )

        return query.order_by(AtendidoSchema.nome).limit(20).all()

    def buscar_orientacoes_por_atendido(self, busca: str, page_params: PageParams):
        query = (
            self.session.query(OrientacaoJuridicaSchema)
            .filter(OrientacaoJuridicaSchema.status)
            .outerjoin(
                Atendido_xOrientacaoJuridicaSchema,
                OrientacaoJuridicaSchema.id
                == Atendido_xOrientacaoJuridicaSchema.id_orientacaoJuridica,
            )
            .outerjoin(
                AtendidoSchema,
                AtendidoSchema.id == Atendido_xOrientacaoJuridicaSchema.id_atendido,
            )
            .filter(
                or_(
                    AtendidoSchema.nome.contains(busca),
                    AtendidoSchema.cpf.contains(busca),
                )
            )
            .order_by(OrientacaoJuridicaSchema.data_criacao.desc())
        )

        total = query.count()
        page = page_params["page"]
        per_page = page_params["per_page"]
        items = query.offset((page - 1) * per_page).limit(per_page).all()

        from gestaolegal.repositories.base_repository import PaginatedResult

        return PaginatedResult(
            items=[self._build_model(e) for e in items],
            total=total,
            page=page,
            per_page=per_page,
        )

    def associate_atendido(self, orientacao_id: int, atendido_id: int) -> bool:
        try:
            orientacao = self.find_by_id(orientacao_id)
            if not orientacao:
                return False

            existing = (
                self.session.query(Atendido_xOrientacaoJuridicaSchema)
                .filter_by(id_orientacaoJuridica=orientacao_id, id_atendido=atendido_id)
                .first()
            )
            if existing:
                return False

            association = Atendido_xOrientacaoJuridicaSchema(
                id_orientacaoJuridica=orientacao_id,
                id_atendido=atendido_id,
            )
            self.session.add(association)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def disassociate_atendido(self, orientacao_id: int, atendido_id: int) -> bool:
        try:
            association = (
                self.session.query(Atendido_xOrientacaoJuridicaSchema)
                .filter_by(id_orientacaoJuridica=orientacao_id, id_atendido=atendido_id)
                .first()
            )
            if not association:
                return False

            self.session.delete(association)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def associate_assistencia_judiciaria(
        self, orientacao_id: int, assistencia_id: int
    ) -> bool:
        try:
            orientacao = self.find_by_id(orientacao_id)
            if not orientacao:
                return False

            from gestaolegal.schemas.assistencia_judiciaria import (
                AssistenciaJudiciariaSchema,
            )

            assistencia = (
                self.session.query(AssistenciaJudiciariaSchema)
                .filter_by(id=assistencia_id, status=True)
                .first()
            )
            if not assistencia:
                return False

            existing = (
                self.session.query(AssistenciaJudiciaria_xOrientacaoJuridicaSchema)
                .filter_by(
                    id_orientacaoJuridica=orientacao_id,
                    id_assistenciaJudiciaria=assistencia_id,
                )
                .first()
            )
            if existing:
                return False

            association = AssistenciaJudiciaria_xOrientacaoJuridicaSchema(
                id_orientacaoJuridica=orientacao_id,
                id_assistenciaJudiciaria=assistencia_id,
            )
            self.session.add(association)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def _create_paginated_result(self, items, total, page_params):
        from gestaolegal.repositories.base_repository import PaginatedResult

        return PaginatedResult(
            items, total, page_params["page"] or 1, page_params["per_page"] or total
        )
