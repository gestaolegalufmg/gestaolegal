from dataclasses import dataclass
from datetime import date, datetime


class Confirmacao:
    """Estado de conferência de uma presença ou de um dia de plantão marcado."""

    ABERTO = "aberto"
    # Os três estados que a conferência pode atribuir estão declarados como
    # Literal em ConfirmacaoItemInput, que valida a entrada da API.
    CONFIRMAR = "confirmar"
    DIVERGENCIA = "divergencia"
    AUSENCIA = "ausencia"


# Vagas por dia de plantão, por papel. Papéis ausentes não têm limite.
VAGAS_POR_UROLE = {
    "orient": 1,
    "estag_direito": 3,
}

# Quantos dias de plantão cada pessoa pode marcar por período.
LIMITE_MARCACOES = 2
LIMITE_MARCACOES_POR_UROLE = {
    "orient": 1,
}

# Papéis que podem marcar plantão mesmo com o período fechado.
UROLES_IGNORAM_JANELA = ("admin", "colab_proj")


@dataclass
class Plantao:
    """Janela de marcação do plantão. Há uma única linha na tabela."""

    id: int | None = None
    data_abertura: datetime | None = None
    data_fechamento: datetime | None = None
    unidade_id: int | None = None


@dataclass
class DiaPlantao:
    """Dia aberto para plantão. `status=False` = removido da configuração."""

    data: date
    status: bool = True
    id: int | None = None
    unidade_id: int | None = None


@dataclass
class DiaMarcadoPlantao:
    """Dia de plantão escolhido por uma pessoa. `status=False` = apagado."""

    data_marcada: date
    id_usuario: int
    confirmacao: str = Confirmacao.ABERTO
    status: bool = True
    id: int | None = None
    unidade_id: int | None = None
