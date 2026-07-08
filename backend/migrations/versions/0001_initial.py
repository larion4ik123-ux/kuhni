"""Initial migration — all tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Базовые сущности (без FK) ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("note", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "media_files",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("category", sa.String(32), index=True, nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("stored_path", sa.String(512), nullable=False),
        sa.Column("webp_path", sa.String(512), nullable=True),
        sa.Column("jpg_path", sa.String(512), nullable=True),
        sa.Column("mime", sa.String(64), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("sha256", sa.String(64), index=True, nullable=True),
        sa.Column("is_real_work", sa.Boolean(), default=False, nullable=False),
        sa.Column("focus_x", sa.Float(), default=0.5, nullable=False),
        sa.Column("focus_y", sa.Float(), default=0.5, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "funnel_questions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(32), index=True, nullable=False),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("order", sa.Integer(), default=0, index=True, nullable=False),
        sa.Column("required", sa.Boolean(), default=True, nullable=False),
        sa.Column("active", sa.Boolean(), default=True, index=True, nullable=False),
        sa.Column("allow_skip", sa.Boolean(), default=False, nullable=False),
        sa.Column("generation_key", sa.String(64), nullable=True),
        sa.Column("condition", sa.JSON(), nullable=True),
        sa.Column("next_question_rule", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "funnel_options",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("funnel_questions.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("internal_code", sa.String(64), index=True, nullable=False),
        sa.Column("generation_hint", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), default=True, nullable=False),
        sa.Column("order", sa.Integer(), default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "site_blocks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("media_file_id", sa.Integer(), nullable=True),
        sa.Column("order", sa.Integer(), default=0, nullable=False),
        sa.Column("visible", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "faq_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("question", sa.String(255), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), default=0, index=True, nullable=False),
        sa.Column("visible", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "process_steps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("display_order", sa.Integer(), default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "gallery_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("caption", sa.String(255), nullable=True),
        sa.Column("layout", sa.String(32), index=True, nullable=True),
        sa.Column("style", sa.String(32), index=True, nullable=True),
        sa.Column("primary_color", sa.String(32), nullable=True),
        sa.Column("alt_text", sa.String(255), nullable=True),
        sa.Column("display_order", sa.Integer(), default=0, nullable=False),
        sa.Column("is_real_work", sa.Boolean(), default=True, nullable=False),
        sa.Column("visible", sa.Boolean(), default=True, index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("author_name", sa.String(128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review_date", sa.String(32), nullable=True),
        sa.Column("source", sa.String(32), default="manual", nullable=False),
        sa.Column("source_url", sa.String(512), nullable=True),
        sa.Column("display_order", sa.Integer(), default=0, nullable=False),
        sa.Column("visible", sa.Boolean(), default=True, index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(64), unique=True, index=True, nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("category", sa.String(32), default="general", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # --- Сущности с FK на users ---
    op.create_table(
        "user_contacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("phone", sa.String(32), index=True, nullable=False),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("source", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_contacts_user_created", "user_contacts", ["user_id", "created_at"])

    op.create_table(
        "messenger_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("messenger", sa.String(16), index=True, nullable=False),
        sa.Column("account_id", sa.String(64), nullable=False),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("messenger", "account_id", name="uq_messenger_account"),
    )

    op.create_table(
        "funnel_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("messenger_account_id", sa.Integer(), sa.ForeignKey("messenger_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), index=True, nullable=False, default="in_progress"),
        sa.Column("source", sa.String(64), index=True, nullable=False, default="unknown"),
        sa.Column("current_question_id", sa.Integer(), sa.ForeignKey("funnel_questions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "funnel_answers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("funnel_sessions.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("funnel_questions.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("option_ids", sa.JSON(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_number", sa.Float(), nullable=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admins.id", ondelete="SET NULL"), index=True, nullable=True),
        sa.Column("action", sa.String(64), index=True, nullable=False),
        sa.Column("target_type", sa.String(64), nullable=True),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
    )

    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("buttons", sa.JSON(), nullable=True),
        sa.Column("segment", sa.String(32), default="all", nullable=False),
        sa.Column("status", sa.String(32), index=True, nullable=False, default="draft"),
        sa.Column("total", sa.Integer(), default=0, nullable=False),
        sa.Column("sent", sa.Integer(), default=0, nullable=False),
        sa.Column("failed", sa.Integer(), default=0, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "broadcast_recipients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("broadcast_id", sa.Integer(), sa.ForeignKey("broadcasts.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("messenger_account_id", sa.Integer(), sa.ForeignKey("messenger_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), default="pending", nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("type", sa.String(32), index=True, nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(32), index=True, nullable=False, default="pending"),
        sa.Column("attempts", sa.Integer(), default=0, nullable=False),
        sa.Column("max_attempts", sa.Integer(), default=3, nullable=False),
        sa.Column("run_after", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="SET NULL"), index=True, nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("funnel_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), index=True, nullable=False, default="pending"),
        sa.Column("provider", sa.String(64), nullable=False, default="mock"),
        sa.Column("model", sa.String(128), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("params", sa.JSON(), nullable=True),
        sa.Column("result_media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True),
        sa.Column("attempt", sa.Integer(), default=0, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "generated_images",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("generation_jobs.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="SET NULL"), nullable=True),
        sa.Column("variant_index", sa.Integer(), default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("funnel_sessions.id", ondelete="SET NULL"), index=True, nullable=True),
        sa.Column("phone", sa.String(32), index=True, nullable=True),
        sa.Column("status", sa.String(32), index=True, nullable=False, default="new"),
        sa.Column("source", sa.String(64), index=True, nullable=False, default="unknown"),
        sa.Column("selection_description", sa.Text(), nullable=True),
        sa.Column("generation_job_id", sa.Integer(), sa.ForeignKey("generation_jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("manager_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "lead_status_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("old_status", sa.String(32), nullable=True),
        sa.Column("new_status", sa.String(32), nullable=False),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    # Удаляем в обратном порядке (FK сначала)
    op.drop_table("lead_status_history")
    op.drop_table("leads")
    op.drop_table("generated_images")
    op.drop_table("generation_jobs")
    op.drop_table("jobs")
    op.drop_table("broadcast_recipients")
    op.drop_table("broadcasts")
    op.drop_table("audit_logs")
    op.drop_table("funnel_answers")
    op.drop_table("funnel_sessions")
    op.drop_table("messenger_accounts")
    op.drop_table("user_contacts")
    op.drop_table("settings")
    op.drop_table("reviews")
    op.drop_table("gallery_items")
    op.drop_table("process_steps")
    op.drop_table("faq_items")
    op.drop_table("site_blocks")
    op.drop_table("funnel_options")
    op.drop_table("funnel_questions")
    op.drop_table("media_files")
    op.drop_table("admins")
    op.drop_table("users")
