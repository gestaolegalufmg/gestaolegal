import logging
import secrets
import string
from datetime import datetime
from typing import Any, TypeVar

from flask_bcrypt import Bcrypt

from gestaolegal.common import PageParams
from gestaolegal.models.endereco import Endereco
from gestaolegal.models.user import User
from gestaolegal.repositories.base_repository import BaseRepository, WhereConditions
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.schemas.endereco import EnderecoSchema

T = TypeVar("T")

logger = logging.getLogger(__name__)


class UsuarioService:
    repository: UserRepository
    endereco_repository: BaseRepository[EnderecoSchema, Endereco]

    def __init__(self):
        self.repository = UserRepository()
        self.endereco_repository = BaseRepository(EnderecoSchema, Endereco)

    def find_by_id(self, id: int) -> User | None:
        return self.repository.find_by_id(id)

    def find_by_email(self, email: str) -> User | None:
        return self.repository.find(where_conditions=("email", "eq", email))

    def search(self, search: str = "", page_params: PageParams | None = None, role: str = "all", show_inactive: bool = False):
        where_conditions: WhereConditions = []

        if role != "all":
            where_conditions.append(("urole", "eq", role))

        if search:
            where_conditions.append(("nome", "ilike", f"%{search}%"))

        return self.repository.get(
            page_params=page_params, order_by=["nome"], where_conditions=where_conditions, active_only=not show_inactive
        )

    def search_users_by_filters(
        self,
        valor_busca: str = "",
        funcao: str = "all",
        status: str = "1",
        page_params: PageParams | None = None,
    ):
        return self.repository.search(valor_busca, funcao, status, page_params)

    def get_users_by_filters(
        self, funcao: str | None = None, status: str | None = None
    ):
        filters: WhereConditions = []

        if status:
            filters.append(("status", "eq", status == "1"))

        if funcao and funcao != "all":
            filters.append(("urole", "eq", funcao))

        return self.repository.get(where_conditions=filters)

    def authenticate_user(self, email: str, senha: str) -> User | None:
        user = self.repository.find(where_conditions=("email", "eq", email))
        if not user:
            logger.info(f"User not found: {email}")
            return None

        if self.check_password(user, senha):
            logger.info(f"User authenticated successfully: {email}")
            return user

        logger.warning(f"Invalid password for user: {email}")
        return None

    def authenticate(self, email: str, senha: str) -> User | None:
        user = self.find_by_email(email)
        if not user:
            return None
        if self.check_password(user, senha):
            return user
        return None

    def check_password(self, user: User, senha: str) -> bool:
        bcrypt = Bcrypt()
        return bcrypt.check_password_hash(user.senha, senha)

    def create(self, user_data: dict[str, Any], criado_por: int) -> User:
        endereco_data = self.__extract_endereco_data(user_data)
        endereco = self.endereco_repository.create(endereco_data)


        user_data["endereco_id"] = endereco.id
        user_data["criadopor"] = criado_por

        bcrypt = Bcrypt()

        password_length = 12
        alphabet = string.ascii_letters + string.digits
        random_password = ''.join(secrets.choice(alphabet) for _ in range(password_length))
        user_data["senha"] = bcrypt.generate_password_hash(random_password).decode("utf-8")

        return self.repository.create(User(**user_data))

    def update(
        self,
        user_id: int,
        user_data: dict[str, Any],
        modificado_por: int | None,
    ) -> User | None:
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        endereco = user.endereco
        endereco_data = self.__extract_endereco_data(user_data)
        if not endereco:
            raise ValueError(f"User with id {user_id} does not have an endereco")

        _ = self.endereco_repository.update(user.endereco_id, Endereco(**endereco_data))

        user_data["modificado"] = datetime.now()
        user_data["modificadopor"] = modificado_por

        logger.info(f"Existing data: {user.to_dict()}")
        existing_data = user.to_dict(with_endereco=False)
        existing_data.update(user_data)

        logger.info(f"Updated data to be saved: {existing_data}")
        return self.repository.update(user_id, User(**existing_data))

    def soft_delete(self, user_id: int) -> bool:
        return self.repository.soft_delete(user_id)

    def change_password(
        self,
        user_id: int,
        current_password: str | None,
        new_password: str,
        is_admin_change: bool = False
    ) -> User | None:
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        if not is_admin_change and current_password:
            if not self.check_password(user, current_password):
                raise ValueError("Current password is incorrect")

        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        user_data = user.to_dict(with_endereco=False)
        user_data["senha"] = hashed_password
        user_data["modificado"] = datetime.now()

        return self.repository.update(user_id, User(**user_data))

    def __extract_endereco_data(self, user_data: dict[str, Any]):
        user_data.pop("endereco_id")
        return {
            "logradouro": user_data.pop("logradouro"),
            "numero": user_data.pop("numero"),
            "cidade": user_data.pop("cidade"),
            "estado": user_data.pop("estado"),
            "complemento": user_data.pop("complemento"),
            "bairro": user_data.pop("bairro"),
            "cep": user_data.pop("cep"),
        }
