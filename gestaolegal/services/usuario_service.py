import logging
from datetime import datetime
from typing import TypeVar

from flask import current_app
from flask_bcrypt import Bcrypt
from itsdangerous import Serializer, URLSafeTimedSerializer

from gestaolegal.common import PageParams
from gestaolegal.common.constants import UserRole
from gestaolegal.models.usuario import Usuario
from gestaolegal.repositories.base_repository import WhereConditions
from gestaolegal.repositories.user_repository import UserRepository
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.services.endereco_service import EnderecoService

T = TypeVar("T")

logger = logging.getLogger(__name__)


class UsuarioService:
    repository: UserRepository
    endereco_service: EnderecoService

    def __init__(self):
        self.repository = UserRepository()
        self.endereco_service = EnderecoService()

    def find_by_id(self, id: int) -> Usuario | None:
        return self.repository.find_by_id(id)

    def find_by_email(self, email: str) -> Usuario | None:
        return self.repository.find(where_conditions=("email", "eq", email))

    def find_by_id_with_inactive(self, id: int) -> Usuario | None:
        return self.repository.find_by_id(id, active_only=False)

    def find_by_email_with_inactive(self, email: str) -> Usuario | None:
        return self.repository.find(where_conditions=("email", "eq", email), active_only=False)

    def get_all(self, page_params: PageParams | None = None):
        return self.repository.get(
            page_params=page_params, order_by=["nome"]
        )

    def search_by_name(self, string: str, page_params: PageParams | None = None):
        return self.repository.search_by_name(string, page_params)

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

    def authenticate_user(self, email: str, senha: str) -> Usuario | None:
        usuario = self.repository.find(where_conditions=("email", "eq", email))
        if not usuario:
            logger.info(f"User not found: {email}")
            return None

        if self.check_password(usuario, senha):
            logger.info(f"User authenticated successfully: {email}")
            return usuario

        logger.warning(f"Invalid password for user: {email}")
        return None

    def check_password(self, usuario: Usuario, senha: str) -> bool:
        bcrypt = Bcrypt()
        return bcrypt.check_password_hash(usuario.senha, senha)

    def create(self, user_data: dict, criado_por: int) -> Usuario:
        user_data.pop("csrf_token")
        endereco_data = {
            "logradouro": user_data.pop("logradouro"),
            "numero": user_data.pop("numero"),
            "complemento": user_data.pop("complemento"),
            "bairro": user_data.pop("bairro"),
            "cep": user_data.pop("cep"),
        }
        endereco = self.endereco_service.create_or_update_from_data(endereco_data)

        if "bolsista" in user_data:
            user_data["bolsista"] = user_data["bolsista"]
            if user_data["bolsista"]:
                user_data["inicio_bolsa"] = user_data.get("inicio_bolsa")
                user_data["fim_bolsa"] = user_data.get("fim_bolsa")
                user_data["tipo_bolsa"] = user_data.get("tipo_bolsa")
            else:
                user_data["inicio_bolsa"] = None
                user_data["fim_bolsa"] = None
                user_data["tipo_bolsa"] = None

        user_data["endereco_id"] = endereco.id
        user_data["criado"] = datetime.now()
        user_data["criadopor"] = criado_por
        user_data["status"] = True

        bcrypt = Bcrypt()

        user_data["senha"] = bcrypt.generate_password_hash(user_data["senha"]).decode(
            "utf-8"
        )

        return self.repository.create(user_data)

    def update(
        self, user_id: int, user_data: dict, modificado_por: int | None
    ) -> Usuario | None:
        usuario = self.repository.find_by_id(user_id)
        if not usuario:
            raise ValueError(f"Usuario with id {user_id} not found")

        user_data.pop("csrf_token")
        endereco_data = {
            "logradouro": user_data.pop("logradouro"),
            "numero": user_data.pop("numero"),
            "complemento": user_data.pop("complemento"),
            "bairro": user_data.pop("bairro"),
            "cep": user_data.pop("cep"),
        }

        endereco = self.endereco_service.create_or_update_from_data(
            endereco_data, usuario.endereco_id
        )
        user_data["endereco_id"] = endereco.id

        if "bolsista" in user_data:
            user_data["bolsista"] = user_data["bolsista"]
            if user_data["bolsista"]:
                user_data["inicio_bolsa"] = user_data.get("inicio_bolsa")
                user_data["fim_bolsa"] = user_data.get("fim_bolsa")
                user_data["tipo_bolsa"] = user_data.get("tipo_bolsa")
            else:
                user_data["inicio_bolsa"] = None
                user_data["fim_bolsa"] = None
                user_data["tipo_bolsa"] = None

        if "senha" in user_data and (
            user_data["senha"] is None or user_data["senha"] == ""
        ):
            user_data.pop("senha")

        user_data["modificado"] = datetime.now()
        user_data["modificadopor"] = modificado_por

        return self.repository.update(user_id, user_data)

    def update_password(
        self, user_id: int, new_password: str, from_admin: bool = False
    ) -> bool:
        if not self.repository.find_by_id(user_id):
            return False

        bcrypt = Bcrypt()
        update_data = {
            "senha": bcrypt.generate_password_hash(new_password).decode("utf-8")
        }

        if from_admin:
            update_data["chave_recuperacao"] = False

        return self.repository.update(user_id, update_data) is not None

    def soft_delete(self, user_id: int) -> bool:
        return self.repository.soft_delete(user_id)

    def set_password_recovery(self, email: str) -> bool:
        usuario = self.repository.find(where_conditions=[("email", "eq", email)])
        if not usuario:
            return False

        return (
            self.repository.update(usuario.id, {"chave_recuperacao": True}) is not None
        )

    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        try:
            s = Serializer(current_app.config["SECRET_KEY"])
            user_id = s.loads(token)["user_id"]
            usuario = self.repository.find_by_id(user_id)

            if not usuario or not usuario.chave_recuperacao:
                return False

            bcrypt = Bcrypt()
            update_data = {
                "senha": bcrypt.generate_password_hash(new_password).decode("utf-8"),
                "chave_recuperacao": False,
            }

            return self.repository.update(usuario.id, update_data) is not None
        except Exception:
            return False

    def validate_user_permissions(
        self,
        user_id: int,
        current_user_id: int,
        current_user_role: UserRole,
        admin_padrao_id: int,
    ) -> tuple[bool, str]:
        if (
            current_user_role not in [UserRole.ADMINISTRADOR, UserRole.PROFESSOR]
            and current_user_id != user_id
        ):
            return False, "Você não tem permissão para editar outro usuário."

        if user_id == admin_padrao_id and current_user_id != admin_padrao_id:
            return False, "O administrador padrão só pode ser alterado por si próprio."

        return True, ""

    def validate_user_status(self, user_id: int) -> tuple[bool, str]:
        usuario = self.repository.find_by_id(user_id)
        if not usuario:
            return False, "Usuário não encontrado."

        if not usuario.status:
            return False, "Este usuário está inativo."

        return True, ""

    def token_recovery(self, user_id: int, expires_in: int = 3600) -> str:
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": user_id}, salt="recovery")

    def verify_token(self, token: str, max_age: int = 3600) -> Usuario | None:
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, salt="recovery", max_age=max_age)["user_id"]
        except:
            return None
        return self.repository.find_by_id(user_id)

    def validate_password(self, senha: str) -> tuple[bool, str]:
        caracteresEspeciais = [".", ",", ";", "@", "#"]

        if len(senha) < 6:
            return False, "Sua senha deve conter pelo menos 6 caracteres."

        if not any(char.isdigit() for char in senha):
            return False, "Sua senha precisa conter pelo menos um número."

        if not any(char.isupper() for char in senha):
            return False, "Sua senha precisa conter pelo menos uma letra maiúscula."

        if not any(char in caracteresEspeciais for char in senha):
            return (
                False,
                "Sua senha precisa conter pelo menos um caractere especial, sendo eles: '.' ',' ';' '@','#' .",
            )

        if not any(char.isalpha() for char in senha):
            return False, "Sua senha precisa conter pelo menos uma letra do alfabeto."

        return True, ""

    def process_login(self, login: str, senha: str) -> Usuario:
        usuario = self.authenticate_user(login, senha)
        if not usuario:
            raise ValueError("Login ou senha inválidos")
        return usuario

    def process_password_recovery(self, email: str) -> bool:
        if not self.set_password_recovery(email):
            raise ValueError("Email não encontrado no sistema")
        return True

    def validate_password_reset_token(self, token: str) -> Usuario:
        usuario = self.verify_token(token)
        if not usuario or not usuario.chave_recuperacao:
            raise ValueError("Token inválido ou expirado")
        return usuario
