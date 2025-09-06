import logging
from datetime import datetime
from typing import Any, Callable, TypeVar

from flask_bcrypt import Bcrypt
from sqlalchemy.orm import Query

from gestaolegal.common.constants import UserRole
from gestaolegal.forms.usuario import EditarUsuarioForm, EnderecoForm
from gestaolegal.models.usuario import Usuario
from gestaolegal.schemas.endereco import EnderecoSchema
from gestaolegal.schemas.usuario import UsuarioSchema
from gestaolegal.services.base_service import BaseService

T = TypeVar("T")

logger = logging.getLogger(__name__)


class UsuarioService(BaseService[UsuarioSchema, Usuario]):
    def __init__(self):
        super().__init__(UsuarioSchema)

    def find_by_id(self, id: int) -> Usuario | None:
        usuario_schema = (
            self.filter_active(self.session.query(UsuarioSchema))
            .filter(UsuarioSchema.id == id)
            .first()
        )
        return Usuario.from_sqlalchemy(usuario_schema) if usuario_schema else None

    def find_by_email(self, email: str) -> Usuario | None:
        logger.info(f"UsuarioService.find_by_email called for: {email}")
        usuario_schema = (
            self.filter_active(self.session.query(UsuarioSchema))
            .filter(UsuarioSchema.email == email)
            .first()
        )
        return Usuario.from_sqlalchemy(usuario_schema) if usuario_schema else None

    def find_by_id_with_inactive(self, id: int) -> Usuario | None:
        usuario_schema = (
            self.session.query(UsuarioSchema).filter(UsuarioSchema.id == id).first()
        )
        return Usuario.from_sqlalchemy(usuario_schema) if usuario_schema else None

    def find_by_email_with_inactive(self, email: str) -> Usuario | None:
        usuario_schema = (
            self.session.query(UsuarioSchema)
            .filter(UsuarioSchema.email == email)
            .first()
        )
        return Usuario.from_sqlalchemy(usuario_schema) if usuario_schema else None

    def get_all(self, paginator: Callable[..., Any] | None = None):
        query = self.filter_active(self.session.query(UsuarioSchema)).order_by(
            UsuarioSchema.nome
        )

        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                result.items = [Usuario.from_sqlalchemy(item) for item in result.items]
                return result
            else:
                return [Usuario.from_sqlalchemy(item) for item in result]

        usuarios_schema = query.all()
        return [Usuario.from_sqlalchemy(usuario) for usuario in usuarios_schema]

    def search_by_str(self, string: str, paginator: Callable[..., Any] | None = None):
        result = (
            self.session.query(UsuarioSchema)
            .filter(UsuarioSchema.nome.ilike(f"%{string}%"))
            .order_by(UsuarioSchema.nome)
        )

        if paginator:
            paginated_result = paginator(result)
            if hasattr(paginated_result, "items"):
                paginated_result.items = [
                    Usuario.from_sqlalchemy(item) for item in paginated_result.items
                ]
                return paginated_result
            else:
                return [Usuario.from_sqlalchemy(item) for item in paginated_result]

        usuarios_schema = result.all()
        return [Usuario.from_sqlalchemy(usuario) for usuario in usuarios_schema]

    def search_users_by_filters(
        self,
        valor_busca: str = "",
        funcao: str = "all",
        status: str = "1",
        paginator: Callable[..., Any] | None = None,
    ):
        query = self.session.query(UsuarioSchema)

        if funcao != "all":
            query = query.filter(UsuarioSchema.urole == funcao)

        query = query.filter(UsuarioSchema.status == (status == "1"))

        if valor_busca:
            query = query.filter(UsuarioSchema.nome.ilike(f"%{valor_busca}%"))

        query = query.order_by(UsuarioSchema.nome)

        if paginator:
            result = paginator(query)
            if hasattr(result, "items"):
                result.items = [Usuario.from_sqlalchemy(item) for item in result.items]
                return result
            else:
                return [Usuario.from_sqlalchemy(item) for item in result]

        usuarios = query.all()
        return [Usuario.from_sqlalchemy(usuario) for usuario in usuarios]

    def get_users_by_filters_ajax(self, funcao: str = None, status: str = None):
        """Get users by filters for AJAX requests"""
        if funcao and status:
            if funcao != "all":
                usuarios = self.session.query(UsuarioSchema).filter(
                    UsuarioSchema.urole == funcao,
                    UsuarioSchema.status == (status == "1"),
                )
            else:
                usuarios = self.session.query(UsuarioSchema).filter(
                    UsuarioSchema.status == (status == "1")
                )
        else:
            if status:
                usuarios = self.session.query(UsuarioSchema).filter(
                    UsuarioSchema.status == (status == "1")
                )
            else:
                usuarios = self.session.query(UsuarioSchema).filter(
                    UsuarioSchema.status
                )

        usuarios = usuarios.all()
        return [Usuario.from_sqlalchemy(usuario) for usuario in usuarios]

    def authenticate_user(self, email: str, senha: str) -> Usuario | None:
        logger.info(f"UsuarioService.authenticate_user called for: {email}")
        usuario_schema = (
            self.session.query(UsuarioSchema).filter_by(email=email).first()
        )
        if usuario_schema:
            usuario = Usuario.from_sqlalchemy(usuario_schema)
            if Usuario.checa_senha(usuario, senha):
                logger.info(f"User authenticated successfully: {email}")
                return usuario
            else:
                logger.warning(f"Invalid password for user: {email}")
        else:
            logger.warning(f"User not found: {email}")
        return None

    def create_user(
        self, user_data: dict, endereco_data: dict, criado_por: int
    ) -> Usuario:
        logger.info(
            f"UsuarioService.create_user called for: {user_data.get('email', 'Unknown')}"
        )
        entidade_endereco = EnderecoSchema(**endereco_data)
        self.session.add(entidade_endereco)
        self.session.flush()

        user_data["endereco_id"] = entidade_endereco.id
        user_data["criado"] = datetime.now()
        user_data["criadopor"] = criado_por
        user_data["status"] = True

        entidade_usuario_schema = UsuarioSchema(**user_data)

        bcrypt = Bcrypt()
        entidade_usuario_schema.senha = bcrypt.generate_password_hash(
            user_data["senha"]
        ).decode("utf-8")

        if "bolsista" in user_data:
            entidade_usuario_schema.bolsista = user_data["bolsista"]
            if user_data["bolsista"]:
                entidade_usuario_schema.inicio_bolsa = user_data.get("inicio_bolsa")
                entidade_usuario_schema.fim_bolsa = user_data.get("fim_bolsa")
                entidade_usuario_schema.tipo_bolsa = user_data.get("tipo_bolsa")
            else:
                entidade_usuario_schema.inicio_bolsa = None
                entidade_usuario_schema.fim_bolsa = None
                entidade_usuario_schema.tipo_bolsa = None

        self.session.add(entidade_usuario_schema)
        self.session.commit()

        # Return the model object
        return Usuario.from_sqlalchemy(entidade_usuario_schema)

    def create_user_from_form(self, form, criado_por: int) -> Usuario:
        user_data = EditarUsuarioForm.to_dict(form)
        endereco_data = EnderecoForm.to_dict(form)

        return self.create_user(user_data, endereco_data, criado_por)

    def update_user(
        self, user_id: int, user_data: dict, endereco_data: dict, modificado_por: int
    ) -> Usuario | None:
        usuario_schema = self.session.get(UsuarioSchema, user_id)
        if not usuario_schema:
            return None

        for key, value in user_data.items():
            if hasattr(usuario_schema, key):
                setattr(usuario_schema, key, value)

        if not usuario_schema.endereco:
            entidade_endereco = EnderecoSchema(**endereco_data)
            self.session.add(entidade_endereco)
            self.session.flush()
            usuario_schema.endereco = entidade_endereco
        else:
            for key, value in endereco_data.items():
                if hasattr(usuario_schema.endereco, key):
                    setattr(usuario_schema.endereco, key, value)

        # Update modification fields
        usuario_schema.modificado = datetime.now()
        usuario_schema.modificadopor = modificado_por

        self.session.commit()
        return Usuario.from_sqlalchemy(usuario_schema)

    def update_user_from_form(
        self, user_id: int, form, modificado_por: int
    ) -> Usuario | None:
        user_data = EditarUsuarioForm.to_dict(form)
        endereco_data = EnderecoForm.to_dict(form)

        return self.update_user(user_id, user_data, endereco_data, modificado_por)

    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        usuario_schema = self.session.get(UsuarioSchema, user_id)
        if not usuario_schema:
            return False

        usuario = Usuario.from_sqlalchemy(usuario_schema)
        usuario.setSenha(new_password)
        self.session.commit()
        return True

    def update_password_admin(self, user_id: int, new_password: str) -> bool:
        """Update user password by admin"""
        usuario_schema = self.session.get(UsuarioSchema, user_id)
        if not usuario_schema:
            return False

        bcrypt = Bcrypt()
        usuario_schema.senha = bcrypt.generate_password_hash(new_password)
        usuario_schema.chave_recuperacao = False
        self.session.commit()
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user"""
        usuario_schema = self.session.get(UsuarioSchema, user_id)
        if not usuario_schema:
            return False

        usuario_schema.status = False
        self.session.commit()
        return True

    def set_password_recovery(self, email: str) -> bool:
        """Set password recovery flag for user"""
        usuario_schema = (
            self.session.query(UsuarioSchema).filter_by(email=email).first()
        )
        if not usuario_schema:
            return False

        usuario_schema.chave_recuperacao = True
        self.session.commit()
        return True

    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Reset password using recovery token"""
        usuario = Usuario.verificaToken(token)
        if not usuario or not usuario.chave_recuperacao:
            return False

        bcrypt = Bcrypt()
        usuario_schema = self.session.get(UsuarioSchema, usuario.id)
        usuario_schema.senha = bcrypt.generate_password_hash(new_password)
        usuario_schema.chave_recuperacao = False
        self.session.commit()
        return True

    def validate_email_unique(self, email: str, current_email: str = None) -> bool:
        """Validate if email is unique (excluding current user if updating)"""
        query = self.session.query(UsuarioSchema).filter_by(email=email)
        if current_email and email != current_email:
            existing_user = query.first()
            return existing_user is None
        return True

    def validate_user_permissions(
        self,
        user_id: int,
        current_user_id: int,
        current_user_role: UserRole,
        admin_padrao_id: int,
    ) -> tuple[bool, str]:
        """Validate if current user can edit the target user"""
        if (
            current_user_role not in [UserRole.ADMINISTRADOR, UserRole.PROFESSOR]
            and current_user_id != user_id
        ):
            return False, "Você não tem permissão para editar outro usuário."

        if user_id == admin_padrao_id and current_user_id != admin_padrao_id:
            return False, "O administrador padrão só pode ser alterado por si próprio."

        return True, ""

    def validate_user_status(self, user_id: int) -> tuple[bool, str]:
        """Validate if user exists and is active"""
        usuario_schema = self.session.get(UsuarioSchema, user_id)
        if not usuario_schema:
            return False, "Usuário não encontrado."

        if not usuario_schema.status:
            return False, "Este usuário está inativo."

        return True, ""

    def validate_password(self, senha: str) -> tuple[bool, str]:
        """Validate password strength"""
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

    def filter_active(self, query: Query[T]) -> Query[T]:
        return query.filter(UsuarioSchema.status)
