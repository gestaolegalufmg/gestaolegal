import pytest

from gestaolegal.database.session import get_session, transaction
from gestaolegal.database.tables import orientacao_juridica


class TestTransactionContextManager:
    def test_transaction_commits_on_success_outside_request(self) -> None:
        with transaction() as session:
            result = session.execute(
                orientacao_juridica.insert().values(
                    area_direito="penal",
                    descricao="Test orientacao",
                    status=1,
                    id_usuario=1,
                )
            )
            session.flush()
            orientacao_id = result.lastrowid

        new_session = get_session()
        try:
            result = new_session.execute(
                orientacao_juridica.select().where(
                    orientacao_juridica.c.id == orientacao_id
                )
            ).first()

            assert result is not None
            assert result.descricao == "Test orientacao"
        finally:
            new_session.close()

    def test_transaction_rolls_back_on_error_outside_request(self) -> None:
        initial_session = get_session()
        try:
            initial_result = initial_session.execute(
                orientacao_juridica.select()
            ).fetchall()
            initial_count = len(initial_result)
        finally:
            initial_session.close()

        with pytest.raises(ValueError):
            with transaction() as session:
                session.execute(
                    orientacao_juridica.insert().values(
                        area_direito="penal",
                        descricao="Test orientacao before error",
                        status=1,
                        id_usuario=1,
                    )
                )
                raise ValueError("Simulated error")

        final_session = get_session()
        try:
            final_result = final_session.execute(
                orientacao_juridica.select()
            ).fetchall()
            final_count = len(final_result)
            assert final_count == initial_count
        finally:
            final_session.close()

    def test_nested_operations_rollback_outside_request(self) -> None:
        initial_session = get_session()
        try:
            initial_result = initial_session.execute(
                orientacao_juridica.select()
            ).fetchall()
            initial_count = len(initial_result)
        finally:
            initial_session.close()

        with pytest.raises(ValueError):
            with transaction() as session:
                session.execute(
                    orientacao_juridica.insert().values(
                        area_direito="penal",
                        descricao="First orientacao",
                        status=1,
                        id_usuario=1,
                    )
                )

                session.execute(
                    orientacao_juridica.insert().values(
                        area_direito="civil",
                        descricao="Second orientacao",
                        status=1,
                        id_usuario=1,
                    )
                )

                raise ValueError("Simulated error after multiple creates")

        final_session = get_session()
        try:
            final_result = final_session.execute(
                orientacao_juridica.select()
            ).fetchall()
            final_count = len(final_result)
            assert final_count == initial_count
        finally:
            final_session.close()
