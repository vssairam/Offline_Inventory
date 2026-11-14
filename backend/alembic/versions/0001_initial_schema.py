"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-14
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

now = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index("ix_categories_id", "categories", ["id"])
    op.create_index("ix_categories_user_id", "categories", ["user_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reorder_level", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
        sa.UniqueConstraint("user_id", "sku", name="uq_products_user_sku"),
        sa.CheckConstraint("quantity >= 0", name="ck_products_quantity_nonneg"),
        sa.CheckConstraint(
            "reorder_level >= 0", name="ck_products_reorder_level_nonneg"
        ),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_user_id", "products", ["user_id"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_user_name", "products", ["user_id", "name"])

    op.create_table(
        "sales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "sold_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
    )
    op.create_index("ix_sales_id", "sales", ["id"])
    op.create_index("ix_sales_user_id", "sales", ["user_id"])
    op.create_index("ix_sales_sold_at", "sales", ["sold_at"])

    op.create_table(
        "sale_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sale_id",
            sa.Integer(),
            sa.ForeignKey("sales.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_sale_items_quantity_pos"),
    )
    op.create_index("ix_sale_items_id", "sale_items", ["id"])
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("email_sent", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=now, nullable=False
        ),
    )
    op.create_index("ix_alerts_id", "alerts", ["id"])
    op.create_index("ix_alerts_product_id", "alerts", ["product_id"])
    op.create_index("ix_alerts_user_read", "alerts", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("sale_items")
    op.drop_table("sales")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
