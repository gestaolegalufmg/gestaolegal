"""
Custom exceptions for the Gestão Legal application.

These exceptions provide a structured way to handle different types of errors
throughout the application, making error handling consistent and predictable.
"""

from typing import Any


class GestaoLegalException(Exception):
    """
    Base exception for all application errors.

    All custom exceptions should inherit from this class to allow
    for centralized exception handling.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(GestaoLegalException):
    """
    Raised when a requested resource is not found.

    This should be used instead of returning None or False when a resource
    doesn't exist, allowing for proper 404 HTTP responses.

    Example:
        raise NotFoundException(resource="Caso", resource_id=123)
    """

    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(
            message=f"{resource} não encontrado",
            error_code=f"{resource.upper()}_NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class ValidationException(GestaoLegalException):
    """
    Raised when input validation fails.

    This should be used for business logic validation errors,
    while Pydantic validation errors are handled separately.

    Example:
        raise ValidationException("Email já está em uso", field="email")
    """

    def __init__(self, message: str, field: str | None = None):
        details = {"field": field} if field else {}
        super().__init__(message=message, error_code="VALIDATION_ERROR", details=details)


class UnauthorizedException(GestaoLegalException):
    """
    Raised when a user is not authenticated.

    This should be used for authentication failures (invalid credentials, missing token, etc.)

    Example:
        raise UnauthorizedException("Token inválido ou expirado")
    """

    def __init__(self, message: str = "Não autenticado"):
        super().__init__(message=message, error_code="UNAUTHORIZED")


class ForbiddenException(GestaoLegalException):
    """
    Raised when a user is authenticated but not authorized to perform an action.

    This should be used for authorization failures (insufficient permissions, wrong role, etc.)

    Example:
        raise ForbiddenException("Apenas administradores podem executar esta ação")
    """

    def __init__(self, message: str = "Acesso negado"):
        super().__init__(message=message, error_code="FORBIDDEN")


class BusinessLogicException(GestaoLegalException):
    """
    Raised when business logic rules are violated.

    This should be used for domain-specific errors that don't fit other categories.

    Example:
        raise BusinessLogicException(
            "Caso já foi deferido, não pode ser indeferido",
            error_code="CASO_ALREADY_DEFERRED"
        )
    """

    def __init__(self, message: str, error_code: str):
        super().__init__(message=message, error_code=error_code)


class FileOperationException(GestaoLegalException):
    """
    Raised when file operations fail.

    This should be used for file upload, download, or deletion errors.

    Example:
        raise FileOperationException("Arquivo não encontrado no servidor", operation="download")
    """

    def __init__(self, message: str, operation: str | None = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message, error_code="FILE_OPERATION_ERROR", details=details
        )


class DatabaseException(GestaoLegalException):
    """
    Raised when database operations fail.

    This should be used for database-specific errors that need to be handled
    differently from general exceptions.

    Example:
        raise DatabaseException("Erro ao salvar no banco de dados")
    """

    def __init__(self, message: str = "Erro ao acessar o banco de dados"):
        super().__init__(message=message, error_code="DATABASE_ERROR")


class SetupException(GestaoLegalException):
    """
    Raised when setup operations fail or are misconfigured.

    This should be used for initial system setup errors, such as admin creation
    or configuration issues.

    Example:
        raise SetupException("Configuração de administrador não disponível")
        raise SetupException("Usuário administrador já existe")
    """

    def __init__(self, message: str):
        super().__init__(message=message, error_code="SETUP_ERROR")
