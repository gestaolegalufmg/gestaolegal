from enum import StrEnum


class UserRole(StrEnum):
    """User role enumeration."""

    USER = "user"
    ADMINISTRADOR = "admin"
    ORIENTADOR = "orient"
    COLAB_PROJETO = "colab_proj"
    ESTAGIARIO_DIREITO = "estag_direito"
    COLAB_EXTERNO = "colab_ext"
    PROFESSOR = "prof"

    @property
    def display_name(self) -> str:
        """Return human-readable display name for the role."""
        display_names = {
            "user": "Usuário",
            "admin": "Administrador",
            "orient": "Orientador",
            "colab_proj": "Colaborador de projeto",
            "estag_direito": "Estagiário de Direito",
            "colab_ext": "Colaborador externo",
            "prof": "Professor",
        }
        return display_names.get(self.value, self.value)

    @classmethod
    def get_display_name(cls, role_value: str) -> str:
        """Get display name for a role value string."""
        try:
            role = cls(role_value)
            return role.display_name
        except ValueError:
            return role_value
