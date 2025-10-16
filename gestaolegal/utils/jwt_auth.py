from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from flask import current_app

from gestaolegal.models.user import UserInfo
from gestaolegal.services.usuario_service import UsuarioService


class JWTAuth:
    @staticmethod
    def generate_token(user: UserInfo) -> str:
        now = datetime.now(UTC)
        payload = {
            "user_id": user.id,
            "email": user.email,
            "urole": user.urole,
            "exp": now + timedelta(hours=12),
            "iat": now,
        }

        JWT_SECRET_KEY = str(current_app.config.get("JWT_SECRET_KEY"))

        return jwt.encode(payload, key=JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> dict[str, Any] | None:
        try:
            JWT_SECRET_KEY = str(current_app.config.get("JWT_SECRET_KEY"))
            payload: dict[str, Any] = jwt.decode(
                token, key=JWT_SECRET_KEY, algorithms=["HS256"]
            )

            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_user_from_token(token: str) -> UserInfo | None:
        payload = JWTAuth.verify_token(token)
        if not payload:
            return None

        user_service = UsuarioService()

        user_id: int | None = payload.get("user_id")
        if not user_id:
            return None

        return user_service.find_by_id(user_id)
