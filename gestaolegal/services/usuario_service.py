import logging
import secrets
import string
from datetime import datetime
from typing import Any

from flask_bcrypt import Bcrypt

from gestaolegal.common import PageParams
from gestaolegal.models.user import User
from gestaolegal.models.user_input import UserCreateInput, UserUpdateInput
from gestaolegal.repositories.endereco_repository import EnderecoRepository
from gestaolegal.repositories.pagination_result import PaginatedResult
from gestaolegal.repositories.repository import (
    ComplexWhereClause,
    GetParams,
    WhereClause,
)
from gestaolegal.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UsuarioService:
    repository: UserRepository
    endereco_repository: EnderecoRepository

    def __init__(self):
        self.repository = UserRepository()
        self.endereco_repository = EnderecoRepository()

    def find_by_id(self, id: int) -> User | None:
        logger.info(f"Finding user by id: {id}")
        user = self.repository.find_by_id(id)
        if user:
            if user.endereco_id:
                user.endereco = self.endereco_repository.find_by_id(user.endereco_id)
            logger.info(f"User found with id: {id}")
        else:
            logger.warning(f"User not found with id: {id}")
        return user

    def find_by_email(self, email: str) -> User | None:
        logger.info(f"Finding user by email: {email}")
        user = self.repository.find_by_email(email)
        if user:
            if user.endereco_id:
                user.endereco = self.endereco_repository.find_by_id(user.endereco_id)
            logger.info(f"User found with email: {email}")
        else:
            logger.warning(f"User not found with email: {email}")
        return user

    def search(
        self,
        page_params: PageParams,
        search: str = "",
        role: str = "all",
        show_inactive: bool = False,
    ) -> PaginatedResult[User]:
        logger.info(
            f"Handling search request with params: page_params={page_params}, search='{search}', role='{role}', show_inactive={show_inactive}"
        )
        status = False if show_inactive else True

        clauses: list[WhereClause] = [
            WhereClause(column="status", operator="==", value=status),
        ]

        if search:
            clauses.append(
                WhereClause(column="nome", operator="ilike", value=f"%{search}%")
            )

        if role != "all":
            clauses.append(
                WhereClause(column="urole", operator="ilike", value=f"%{role}%")
            )

        where = (
            ComplexWhereClause(
                clauses=clauses,
                operator="and",
            )
            if len(clauses) > 1
            else clauses[0]
        )

        params = GetParams(
            page_params=page_params,
            where=where,
        )

        logger.info("Performing search with processed params: ", params)
        result = self.repository.search(params=params)

        endereco_ids = [u.endereco_id for u in result.items if u.endereco_id]
        if endereco_ids:
            enderecos = self.endereco_repository.get_by_ids(endereco_ids)
            endereco_map = {e.id: e for e in enderecos}
            for user in result.items:
                if user.endereco_id:
                    user.endereco = endereco_map.get(user.endereco_id)

        logger.info(
            f"Returning result with {result.per_page} of total {result.total} found items"
        )

        return result

    def authenticate(self, email: str, senha: str) -> User | None:
        logger.info(f"Authenticating user with email: {email}")
        user = self.find_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: user not found for email: {email}")
            return None
        if self.check_password(user, senha):
            logger.info(f"Authentication successful for email: {email}")
            return user
        logger.warning(f"Authentication failed: incorrect password for email: {email}")
        return None

    def check_password(self, user: User, senha: str) -> bool:
        bcrypt = Bcrypt()
        return bcrypt.check_password_hash(user.senha, senha)

    def create(self, user_input: UserCreateInput, criado_por: int) -> User:
        logger.info(
            f"Creating user with email: {user_input.email}, role: {user_input.urole}, created by: {criado_por}"
        )
        user_data = user_input.model_dump()

        endereco_data = self.__extract_endereco_data(user_data)
        endereco_id = self.endereco_repository.create(endereco_data)

        user_data["endereco_id"] = endereco_id
        user_data["criadopor"] = criado_por

        bcrypt = Bcrypt()

        password_length = 12
        alphabet = string.ascii_letters + string.digits
        random_password = "".join(
            secrets.choice(alphabet) for _ in range(password_length)
        )
        user_data["senha"] = bcrypt.generate_password_hash(random_password).decode(
            "utf-8"
        )

        user_id = self.repository.create(User(**user_data))
        user = self.find_by_id(user_id)
        if not user:
            logger.error(f"Failed to create user with email: {user_input.email}")
            raise ValueError("Failed to create user")
        logger.info(
            f"User created successfully with id: {user_id}, email: {user_input.email}"
        )
        return user

    def update(
        self,
        user_id: int,
        user_input: UserUpdateInput,
        modificado_por: int | None,
    ) -> User | None:
        logger.info(f"Updating user with id: {user_id}, modified by: {modificado_por}")
        existing = self.repository.find_by_id(user_id)
        if not existing:
            logger.error(f"Update failed: user not found with id: {user_id}")
            raise ValueError(f"User with id {user_id} not found")

        user_data = user_input.model_dump()
        user_data["modificadopor"] = modificado_por
        user_data["modificado"] = datetime.now()

        updated_data = {**existing.model_dump(), **user_data}
        user = User(**updated_data)

        self.repository.update(user_id, user)
        logger.info(f"User updated successfully with id: {user_id}")
        return self.find_by_id(user_id)

    def soft_delete(self, user_id: int) -> bool:
        logger.info(f"Soft deleting user with id: {user_id}")
        result = self.repository.delete(user_id)
        if result:
            logger.info(f"User soft deleted successfully with id: {user_id}")
        else:
            logger.warning(f"Soft delete failed for user with id: {user_id}")
        return result

    def change_password(
        self,
        user_id: int,
        current_password: str | None,
        new_password: str,
        is_admin_change: bool = False,
    ) -> User | None:
        logger.info(
            f"Changing password for user id: {user_id}, is_admin_change: {is_admin_change}"
        )
        user = self.repository.find_by_id(user_id)
        if not user:
            logger.error(f"Password change failed: user not found with id: {user_id}")
            raise ValueError(f"User with id {user_id} not found")

        if not is_admin_change and current_password:
            if not self.check_password(user, current_password):
                logger.warning(
                    f"Password change failed: incorrect current password for user id: {user_id}"
                )
                raise ValueError("Current password is incorrect")

        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        user_data = user.model_dump(exclude={"endereco"})
        user_data["senha"] = hashed_password
        user_data["modificado"] = datetime.now()

        self.repository.update(user_id, User(**user_data))
        logger.info(f"Password changed successfully for user id: {user_id}")
        return self.find_by_id(user_id)

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
