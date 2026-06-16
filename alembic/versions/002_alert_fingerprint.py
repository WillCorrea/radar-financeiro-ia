"""alert fingerprint column

Revision ID: 002_alert_fingerprint
Revises: 001_initial
Create Date: 2026-06-15

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_alert_fingerprint"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("fingerprint", sa.String(length=128), nullable=True))
    op.create_index("ix_alerts_fingerprint", "alerts", ["fingerprint"], unique=False)
    op.create_index("ix_alerts_alert_type_created_at", "alerts", ["alert_type", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_alert_type_created_at", table_name="alerts")
    op.drop_index("ix_alerts_fingerprint", table_name="alerts")
    op.drop_column("alerts", "fingerprint")
