"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-06 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criação das tabelas e tipos
    op.create_table(
        "establishments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_establishments_slug"), "establishments", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("establishment_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "OPERATOR", name="user_role_enum"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["establishment_id"], ["establishments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_establishment_id"), "users", ["establishment_id"], unique=False)

    op.create_table(
        "services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("establishment_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["establishment_id"], ["establishments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_services_establishment_id"), "services", ["establishment_id"], unique=False)

    op.create_table(
        "professionals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("establishment_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("bio", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["establishment_id"], ["establishments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_professionals_establishment_id"), "professionals", ["establishment_id"], unique=False)

    op.create_table(
        "professional_services",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["professional_id"], ["professionals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("professional_id", "service_id", name="uq_professional_service"),
    )

    op.create_table(
        "professional_working_hours",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("break_start_time", sa.Time(), nullable=True),
        sa.Column("break_end_time", sa.Time(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["professional_id"], ["professionals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("professional_id", "day_of_week", name="uq_professional_weekday"),
    )

    op.create_table(
        "professional_unavailabilities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["professional_id"], ["professionals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_professional_unavailabilities_start_datetime"), "professional_unavailabilities", ["start_datetime"], unique=False)

    op.create_table(
        "customers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("establishment_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["establishment_id"], ["establishments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("establishment_id", "phone", name="uq_customer_establishment_phone"),
    )
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=False)
    op.create_index(op.f("ix_customers_establishment_id"), "customers", ["establishment_id"], unique=False)

    op.create_table(
        "appointments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("establishment_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("professional_id", sa.UUID(), nullable=False),
        sa.Column("service_id", sa.UUID(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Enum("SCHEDULED", "CONFIRMED", "CANCELLED", "COMPLETED", "NO_SHOW", name="appointment_status_enum"), nullable=False),
        sa.Column("cancellation_reason", sa.String(length=255), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["establishment_id"], ["establishments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["professional_id"], ["professionals.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_conflict_check", "appointments", ["professional_id", "start_datetime", "end_datetime", "status"], unique=False)
    op.create_index("ix_appointments_establishment_date", "appointments", ["establishment_id", "start_datetime", "status"], unique=False)


def downgrade() -> None:
    op.drop_table("appointments")
    op.execute("DROP TYPE IF EXISTS appointment_status_enum")
    op.drop_table("customers")
    op.drop_table("professional_unavailabilities")
    op.drop_table("professional_working_hours")
    op.drop_table("professional_services")
    op.drop_table("professionals")
    op.drop_table("services")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_role_enum")
    op.drop_table("establishments")
