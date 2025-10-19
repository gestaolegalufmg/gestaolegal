"""
Standardized API response utilities for the Gestão Legal application.

This module provides consistent response wrappers for all API endpoints,
ensuring a uniform structure for both successful and error responses.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from flask import Response, make_response

T = TypeVar("T")


class ApiResponse(Generic[T]):
    """
    Standardized API response wrapper.

    All API responses follow this structure to ensure consistency across
    the application and make frontend integration easier.
    """

    def __init__(
        self,
        success: bool,
        data: T | None = None,
        error: dict[str, Any] | None = None,
        message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.message = message
        self.metadata = metadata

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary for JSON serialization."""
        response_dict: dict[str, Any] = {"success": self.success}

        if self.data is not None:
            response_dict["data"] = self.data

        if self.error is not None:
            response_dict["error"] = self.error

        if self.message is not None:
            response_dict["message"] = self.message

        if self.metadata is not None:
            response_dict["metadata"] = self.metadata

        return response_dict


def success_response(
    data: Any = None,
    message: str | None = None,
    status_code: int = 200,
    include_metadata: bool = False,
) -> Response:
    """
    Create a successful API response.

    Args:
        data: The response data (typically a dict, list, or serialized model)
        message: Optional success message to include
        status_code: HTTP status code (default: 200)
        include_metadata: Whether to include metadata like timestamp

    Returns:
        Flask Response object with standardized success structure

    Example:
        >>> return success_response(data=asdict(caso), message="Caso criado", status_code=201)
        {
            "success": true,
            "data": {"id": 1, "descricao": "..."},
            "message": "Caso criado"
        }
    """
    metadata = None
    if include_metadata:
        metadata = {"timestamp": datetime.utcnow().isoformat()}

    response = ApiResponse(
        success=True, data=data, message=message, metadata=metadata
    )
    return make_response(response.to_dict(), status_code)


def error_response(
    message: str,
    error_code: str | None = None,
    details: dict[str, Any] | None = None,
    status_code: int = 400,
) -> Response:
    """
    Create an error API response.

    Args:
        message: Human-readable error message
        error_code: Machine-readable error code for frontend handling
        details: Additional error details (e.g., validation errors, field names)
        status_code: HTTP status code (default: 400)

    Returns:
        Flask Response object with standardized error structure

    Example:
        >>> return error_response(
        ...     message="Caso não encontrado",
        ...     error_code="CASO_NOT_FOUND",
        ...     status_code=404
        ... )
        {
            "success": false,
            "error": {
                "message": "Caso não encontrado",
                "code": "CASO_NOT_FOUND"
            }
        }
    """
    error_data: dict[str, Any] = {"message": message}

    if error_code:
        error_data["code"] = error_code

    if details:
        error_data["details"] = details

    response = ApiResponse(success=False, error=error_data)
    return make_response(response.to_dict(), status_code)


def paginated_response(
    items: list[Any],
    total: int,
    page: int,
    per_page: int,
    message: str | None = None,
    status_code: int = 200,
) -> Response:
    """
    Create a paginated API response.

    This is a convenience wrapper around success_response for paginated data.

    Args:
        items: List of items for the current page
        total: Total number of items across all pages
        page: Current page number
        per_page: Number of items per page
        message: Optional message
        status_code: HTTP status code (default: 200)

    Returns:
        Flask Response object with paginated data structure

    Example:
        >>> return paginated_response(
        ...     items=[asdict(c) for c in casos],
        ...     total=100,
        ...     page=1,
        ...     per_page=10
        ... )
        {
            "success": true,
            "data": {
                "items": [...],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "per_page": 10,
                    "total_pages": 10,
                    "has_next_page": true,
                    "has_previous_page": false
                }
            }
        }
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next_page": page < total_pages,
            "has_previous_page": page > 1,
        },
    }

    return success_response(data=data, message=message, status_code=status_code)
