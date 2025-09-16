from typing import Any, Optional

from flask import jsonify


def api_success(data: Any = None, status_code: int = 200, **extra: Any):
    payload = {"success": True}

    if data is not None:
        payload["data"] = data
    if extra:
        payload.update(extra)

    return jsonify(payload), status_code


def api_error(
    message: str = "Erro interno do servidor", status_code: int = 400, **extra: Any
):
    payload = {"success": False, "message": message}

    if extra:
        payload.update(extra)

    return jsonify(payload), status_code


def api_paginated(
    items: Any,
    total: Optional[int] = None,
    page: Optional[int] = None,
    pages: Optional[int] = None,
    status_code: int = 200,
    **extra: Any,
):
    payload = {
        "success": True,
        "data": items,
    }

    if total is not None:
        payload["total"] = total
    if page is not None:
        payload["page"] = page
    if pages is not None:
        payload["pages"] = pages
    if extra:
        payload.update(extra)

    return jsonify(payload), status_code
