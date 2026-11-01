
"""add doctor patient status constraint

Revision ID: adb62a078ac1
Revises: 05dc1017d5d2
Create Date: 2026-11-01 17:35:32.706206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'adb62a078ac1'
down_revision: Union[str, Sequence[str], None] = '05dc1017d5d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_check_constraint(
        "check_doctor_patient_status",
        "doctor_patients",
        "status IN ('pending', 'active', 'revoked')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_doctor_patient_status",
        "doctor_patients",
        type_="check",
    )