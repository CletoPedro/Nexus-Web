"""add users table and user_id ownership columns

Revision ID: a68b4885b8dc
Revises: c3d5f6560254
Create Date: 2026-09-08 18:27:09.690969

W12 — Security Foundation.

Data step: if ADMIN_EMAIL and ADMIN_INITIAL_PASSWORD are both set in the
environment at migration time, this creates that user and backfills every
pre-existing row (memories, tasks, documents, inventory_items,
timeline_events) to be owned by them, then enforces user_id NOT NULL on
all five tables.

If those env vars are NOT set, the migration still adds the columns (so
the schema is ready) but leaves user_id nullable and does NOT backfill —
pre-existing rows remain unowned and will not appear for ANY user until
someone is manually assigned to them. This is a deliberate, documented
limitation (see PHASE_W12_REPORT.md) rather than a silent assumption:
we never fabricate a password, and we never guess who "should" own
existing data.
"""
import os
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# Imported directly rather than duplicating bcrypt logic in the migration.
from app.security.hashing import hash_password

# revision identifiers, used by Alembic.
revision: str = 'a68b4885b8dc'
down_revision: Union[str, Sequence[str], None] = 'c3d5f6560254'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OWNED_TABLES = ["memories", "tasks", "documents", "inventory_items", "timeline_events"]


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('must_change_password', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    for table in OWNED_TABLES:
        op.add_column(table, sa.Column('user_id', sa.UUID(), nullable=True))
        op.create_foreign_key(
            f"fk_{table}_user_id_users",
            table,
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE',
        )

    # --- Data step: conditional bootstrap admin + backfill ---
    environment = os.environ.get("ENVIRONMENT", "development").strip().lower()
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD")

    # In production, never migrate existing data into an unowned state.
    # The first production user must be supplied explicitly so the migration
    # can backfill existing rows and enforce ownership in the same transaction.
    if environment != "development" and (not admin_email or not admin_password):
        raise RuntimeError(
            "W12 production migration requires ADMIN_EMAIL and "
            "ADMIN_INITIAL_PASSWORD. Refusing to leave existing data unowned."
        )
    if admin_password is not None and len(admin_password) < 12:
        raise RuntimeError("ADMIN_INITIAL_PASSWORD must contain at least 12 characters.")

    bind = op.get_bind()

    if admin_email and admin_password:
        admin_id = uuid.uuid4()
        hashed = hash_password(admin_password)
        bind.execute(
            sa.text(
                """
                INSERT INTO users (id, email, hashed_password, is_active, must_change_password)
                VALUES (:id, :email, :hashed_password, true, true)
                """
            ),
            {
                "id": admin_id,
                "email": admin_email.strip().lower(),
                "hashed_password": hashed,
            },
        )

        for table in OWNED_TABLES:
            bind.execute(
                sa.text(f"UPDATE {table} SET user_id = :admin_id WHERE user_id IS NULL"),
                {"admin_id": admin_id},
            )
            op.alter_column(table, 'user_id', nullable=False)

        print(
            f"[W12 migration] Bootstrap admin created ({admin_email}); "
            f"must_change_password=true. All pre-existing rows backfilled "
            f"to this user and user_id enforced NOT NULL on: {', '.join(OWNED_TABLES)}."
        )
    else:
        print(
            "[W12 migration] WARNING: ADMIN_EMAIL / ADMIN_INITIAL_PASSWORD not set. "
            "No bootstrap admin was created. Pre-existing rows in "
            f"{', '.join(OWNED_TABLES)} remain unowned (user_id IS NULL) and will not "
            "appear for any user until manually assigned. user_id was NOT made "
            "NOT NULL — re-run a follow-up migration once an owner is assigned."
        )


def downgrade() -> None:
    for table in OWNED_TABLES:
        op.drop_constraint(f"fk_{table}_user_id_users", table, type_='foreignkey')
        op.drop_column(table, 'user_id')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
