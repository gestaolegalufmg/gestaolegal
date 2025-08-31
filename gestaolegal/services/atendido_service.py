from typing import Any, Callable, Literal, TypedDict, TypeVar

from sqlalchemy.orm import Query, Session, scoped_session

from gestaolegal.models.assistido import Assistido as AssistidoModel
from gestaolegal.models.atendido import Atendido as AtendidoModel
from gestaolegal.models.endereco import Endereco
from gestaolegal.plantao.models import AssistidoPessoaJuridica
from gestaolegal.schemas.assistido import AssistidoSchema as Assistido
from gestaolegal.schemas.atendido import AtendidoSchema as Atendido
from gestaolegal.usuario.forms import EnderecoForm

T = TypeVar("T")


class PageParams(TypedDict):
    page: int
    per_page: int


class AtendidoService:
    session: Session | scoped_session[Session]

    def __init__(self, db_session: Session | scoped_session[Session]):
        self.session = db_session

    def find_by_id(self, id: int) -> Atendido | None:
        return (
            self.filter_active(self.session.query(Atendido))
            .filter(Atendido.id == id)
            .first()
        )

    def find_by_email(self, email: str) -> Atendido | None:
        return (
            self.filter_active(self.session.query(Atendido))
            .filter(Atendido.email == email)
            .first()
        )

    def find_atendido_assistido_by_id(
        self, id_atendido: int
    ) -> tuple[AtendidoModel, AssistidoModel] | None:
        result = (
            self.filter_active(self.session.query(Atendido, Assistido))
            .where(Atendido.id == id_atendido)
            .first()
        )

        if not result:
            return None

        atendido_model = AtendidoModel.from_sqlalchemy(result[0]) if result[0] else None
        assistido_model = (
            AssistidoModel.from_sqlalchemy(result[1]) if result[1] else None
        )

        return atendido_model, assistido_model

    def get_atendido_with_assistido_data(
        self, atendido_id: int
    ) -> (
        tuple[AtendidoModel, AssistidoModel | None, AssistidoPessoaJuridica | None]
        | None
    ):
        result = (
            self.filter_active(
                self.session.query(Atendido, Assistido, AssistidoPessoaJuridica)
            )
            .outerjoin(Assistido, onclause=Assistido.id_atendido == Atendido.id)
            .outerjoin(
                AssistidoPessoaJuridica,
                onclause=AssistidoPessoaJuridica.id_assistido == Assistido.id,
            )
            .filter(Atendido.id == atendido_id)
            .first()
        )

        if not result:
            return None

        atendido_model = AtendidoModel.from_sqlalchemy(result[0]) if result[0] else None
        assistido_model = (
            AssistidoModel.from_sqlalchemy(result[1]) if result[1] else None
        )
        assistido_pj = result[2] if result[2] else None

        return atendido_model, assistido_model, assistido_pj

    def get_all(
        self,
        paginator: Callable[..., Any] | None = None,
        include_inactive: bool = False,
    ) -> list[AtendidoModel] | Any:
        query = self.session.query(Atendido).order_by(Atendido.nome)
        if not include_inactive:
            query = self.filter_active(query)

        if paginator:
            return paginator(query)

        results = query.all()
        return [AtendidoModel.from_sqlalchemy(result) for result in results]

    def get_all_atendidos(
        self, paginator: Callable[..., Any] | None = None
    ) -> list[AtendidoModel] | Any:
        query = self.session.query(Atendido).order_by(Atendido.nome)
        if paginator:
            return paginator(query)

        results = query.all()
        return [AtendidoModel.from_sqlalchemy(result) for result in results]

    def get_all_assistidos(
        self, paginator: Callable[..., Any] | None = None
    ) -> list[AssistidoModel] | Any:
        query = self.session.query(Assistido)
        if paginator:
            return paginator(query)

        results = query.all()
        return [AssistidoModel.from_sqlalchemy(result) for result in results]

    def get_inactive(
        self, paginator: Callable[..., Any] | None = None
    ) -> list[AtendidoModel]:
        query = self.session.query(Atendido).order_by(Atendido.nome)

        if paginator:
            return paginator(query)

        results = query.all()
        return [AtendidoModel.from_sqlalchemy(result) for result in results]

    def get_assistidos_by_id_atendido(
        self, atendido_ids: list[int]
    ) -> list[AssistidoModel]:
        results = (
            self.filter_active(self.session.query(Assistido))
            .where(Assistido.id_atendido.in_(atendido_ids))
            .all()
        )

        return [AssistidoModel.from_sqlalchemy(result) for result in results]

    def search_by_str(
        self,
        string: str,
        search_type: Literal["atendidos", "assistidos"] | None = None,
        page_params: PageParams | None = None,
    ) -> list[tuple[AtendidoModel, AssistidoModel | None]]:
        query = self.session.query(Atendido, Assistido)

        if string:
            query = query.filter(
                Atendido.nome.ilike(f"%{string}%")
                | Atendido.cpf.ilike(f"%{string}%")
                | Atendido.cnpj.ilike(f"%{string}%")
            )

        if search_type == "assistidos":
            query = query.filter(Assistido.id.isnot(None))
        elif search_type == "atendidos":
            query = query.filter(Assistido.id.is_(None))

        query = (
            query.order_by(Atendido.nome)
            .offset(page_params["page"] * page_params["per_page"])
            .limit(page_params["per_page"])
        )

        results = query.all()
        return [
            (
                AtendidoModel.from_sqlalchemy(atendido),
                AssistidoModel.from_sqlalchemy(assistido) if assistido else None,
            )
            for atendido, assistido in results
        ]

    def create_endereco(self, form: EnderecoForm) -> Endereco:
        endereco = Endereco(
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cep=form.cep.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
        )

        self.session.add(endereco)
        self.session.commit()
        return endereco

    def create_atendido(self, atendido: AtendidoModel) -> AtendidoModel:
        db_endereco = self.create_endereco(atendido.endereco)
        atendido.endereco_id = db_endereco.id

        db_atendido = Atendido(**atendido.__dict__)
        self.session.add(db_atendido)
        self.session.commit()

        return AtendidoModel.from_sqlalchemy(db_atendido)

    def create_assistido(self, assistido: AssistidoModel) -> AssistidoModel:
        db_assistido = Assistido(**assistido.__dict__)
        self.session.add(db_assistido)
        self.session.commit()

        return AssistidoModel.from_sqlalchemy(db_assistido)

    def delete_atendido(self, atendido_id: int) -> None:
        atendido = self.find_by_id(atendido_id)
        if not atendido:
            raise ValueError("Atendido não encontrado")

        atendido.status = False
        self.session.commit()

    def update_atendido(
        self, atendido_id: int, atendido_data: AtendidoModel
    ) -> AtendidoModel:
        db_atendido = self.find_by_id(atendido_id)
        if not db_atendido:
            raise ValueError("Atendido não encontrado")

        for field in atendido_data.__dict__.keys():
            if hasattr(atendido_data, field):
                setattr(db_atendido, field, getattr(atendido_data, field))

        self.session.commit()
        return AtendidoModel.from_sqlalchemy(db_atendido)

    def update_assistido(
        self, assistido_id: int, assistido_data: AssistidoModel
    ) -> AssistidoModel:
        db_assistido = self.find_by_id(assistido_id)
        if not db_assistido:
            raise ValueError("Assistido não encontrado")

        for field in assistido_data.__dict__.keys():
            if hasattr(assistido_data, field):
                setattr(db_assistido, field, getattr(assistido_data, field))

        self.session.commit()
        return AssistidoModel.from_sqlalchemy(db_assistido)

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(Atendido.status == True)
