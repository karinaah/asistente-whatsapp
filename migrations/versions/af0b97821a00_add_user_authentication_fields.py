"""add user authentication fields

Revision ID: af0b97821a00
Revises: c9910a01ed35
Create Date: 2026-10-18 17:08:31.635551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af0b97821a00'
down_revision: Union[str, Sequence[str], None] = 'c9910a01ed35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agregar campos de autenticación a usuarios."""

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "email",
                sa.String(length=254),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "password_hash",
                sa.String(length=255),
                nullable=True,
            )
        )

        batch_op.create_unique_constraint(
            "uq_users_email",
            ["email"],
        )


def downgrade() -> None:
    """Eliminar campos de autenticación."""

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint(
            "uq_users_email",
            type_="unique",
        )

        batch_op.drop_column("password_hash")
        batch_op.drop_column("email")
