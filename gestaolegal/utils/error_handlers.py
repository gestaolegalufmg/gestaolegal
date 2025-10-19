"""
Centralized error handlers for the Gestão Legal application.

This module registers Flask error handlers that automatically catch and format
all exceptions into standardized API responses, eliminating the need for
try-except blocks in controllers.
"""

import logging

from flask import Flask, Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from gestaolegal.exceptions import (
    BusinessLogicException,
    DatabaseException,
    FileOperationException,
    ForbiddenException,
    GestaoLegalException,
    NotFoundException,
    SetupException,
    UnauthorizedException,
    ValidationException,
)
from gestaolegal.utils.api_response import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """
    Register all error handlers for the Flask application.

    This should be called in the app factory after creating the Flask app instance.

    Args:
        app: The Flask application instance
    """

    @app.errorhandler(NotFoundException)
    def handle_not_found(e: NotFoundException) -> Response:
        """Handle resource not found errors with 404 status."""
        logger.warning(f"Not found: {e.message}", extra={"details": e.details})
        return error_response(
            message=e.message, error_code=e.error_code, details=e.details, status_code=404
        )

    @app.errorhandler(ValidationException)
    def handle_validation_error(e: ValidationException) -> Response:
        """Handle validation errors with 400 status."""
        logger.warning(f"Validation error: {e.message}", extra={"details": e.details})
        return error_response(
            message=e.message, error_code=e.error_code, details=e.details, status_code=400
        )

    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(e: UnauthorizedException) -> Response:
        """Handle authentication errors with 401 status."""
        logger.warning(f"Unauthorized: {e.message}")
        return error_response(message=e.message, error_code=e.error_code, status_code=401)

    @app.errorhandler(ForbiddenException)
    def handle_forbidden(e: ForbiddenException) -> Response:
        """Handle authorization errors with 403 status."""
        logger.warning(f"Forbidden: {e.message}")
        return error_response(message=e.message, error_code=e.error_code, status_code=403)

    @app.errorhandler(BusinessLogicException)
    def handle_business_logic_error(e: BusinessLogicException) -> Response:
        """Handle business logic violations with 422 status."""
        logger.warning(
            f"Business logic error: {e.message}", extra={"details": e.details}
        )
        return error_response(
            message=e.message,
            error_code=e.error_code,
            details=e.details,
            status_code=422,
        )

    @app.errorhandler(FileOperationException)
    def handle_file_operation_error(e: FileOperationException) -> Response:
        """Handle file operation errors with 400 status."""
        logger.error(f"File operation error: {e.message}", extra={"details": e.details})
        return error_response(
            message=e.message, error_code=e.error_code, details=e.details, status_code=400
        )

    @app.errorhandler(DatabaseException)
    def handle_database_error(e: DatabaseException) -> Response:
        """Handle database errors with 500 status."""
        logger.error(f"Database error: {e.message}", exc_info=True)
        return error_response(
            message=e.message, error_code=e.error_code, status_code=500
        )

    @app.errorhandler(SetupException)
    def handle_setup_error(e: SetupException) -> Response:
        """Handle setup/configuration errors with 403 status."""
        logger.warning(f"Setup error: {e.message}")
        return error_response(
            message=e.message, error_code=e.error_code, status_code=403
        )

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation(e: ValidationError) -> Response:
        """
        Handle Pydantic validation errors with 400 status.

        Pydantic validation errors are automatically raised when input models
        fail validation. This handler formats them into a user-friendly response.
        """
        logger.warning(f"Pydantic validation error: {str(e)}")

        errors = []
        for error in e.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return error_response(
            message="Erro de validação nos dados enviados",
            error_code="VALIDATION_ERROR",
            details={"errors": errors},
            status_code=400,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException) -> Response:
        """
        Handle Werkzeug HTTP exceptions (404, 405, etc.).

        These are raised by Flask automatically for various HTTP errors.
        """
        logger.warning(
            f"HTTP exception: {e.code} - {e.description}",
            extra={"code": e.code, "description": e.description},
        )
        return error_response(
            message=e.description or "Erro HTTP",
            error_code=f"HTTP_{e.code}",
            status_code=e.code or 500,
        )

    @app.errorhandler(GestaoLegalException)
    def handle_gestao_legal_exception(e: GestaoLegalException) -> Response:
        """
        Handle any custom GestaoLegalException that wasn't caught by more specific handlers.

        This is a fallback for custom exceptions that don't have their own handler.
        """
        logger.error(
            f"Unhandled GestaoLegalException: {e.message}",
            extra={"error_code": e.error_code, "details": e.details},
            exc_info=True,
        )
        return error_response(
            message=e.message,
            error_code=e.error_code,
            details=e.details,
            status_code=500,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception) -> Response:
        """
        Handle any unhandled exception.

        This is the final fallback that catches all exceptions that weren't
        handled by more specific handlers. It returns a generic error message
        to avoid exposing internal implementation details.
        """
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)

        # Don't expose internal error details in production
        return error_response(
            message="Erro interno do servidor",
            error_code="INTERNAL_ERROR",
            status_code=500,
        )
