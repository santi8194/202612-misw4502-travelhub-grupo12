"""Reconcilia el schema PostgreSQL de catalog hacia UUID nativo."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PgUUID


revision = "002_catalog_uuid_reconcile"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None

UUID_REGEX = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _table_exists(bind: sa.Connection, table_name: str) -> bool:
    return bool(
        bind.execute(
            sa.text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = current_schema()
                      AND table_name = :table_name
                )
                """
            ),
            {"table_name": table_name},
        ).scalar()
    )


def _column_info(bind: sa.Connection, table_name: str, column_name: str) -> dict | None:
    return bind.execute(
        sa.text(
            """
            SELECT data_type, udt_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).mappings().first()


def _constraint_exists(bind: sa.Connection, table_name: str, constraint_name: str) -> bool:
    return bool(
        bind.execute(
            sa.text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints
                    WHERE table_schema = current_schema()
                      AND table_name = :table_name
                      AND constraint_name = :constraint_name
                )
                """
            ),
            {"table_name": table_name, "constraint_name": constraint_name},
        ).scalar()
    )


def _drop_constraint_if_exists(bind: sa.Connection, table_name: str, constraint_name: str) -> None:
    bind.execute(
        sa.text(
            f"ALTER TABLE IF EXISTS {_quote(table_name)} "
            f"DROP CONSTRAINT IF EXISTS {_quote(constraint_name)}"
        )
    )


def _validate_uuid_castable(bind: sa.Connection, table_name: str, column_name: str) -> None:
    q_table = _quote(table_name)
    q_column = _quote(column_name)
    invalid_rows = bind.execute(
        sa.text(
            f"""
            SELECT {q_column}::text AS value
            FROM {q_table}
            WHERE {q_column} IS NOT NULL
              AND NOT ({q_column}::text ~* :uuid_regex)
            LIMIT 5
            """
        ),
        {"uuid_regex": UUID_REGEX},
    ).scalars().all()

    if invalid_rows:
        joined = ", ".join(str(value) for value in invalid_rows)
        raise RuntimeError(
            f"No se puede convertir {table_name}.{column_name} a UUID. "
            f"Valores invalidos de ejemplo: {joined}"
        )


def _alter_column_to_uuid(bind: sa.Connection, table_name: str, column_name: str) -> None:
    info = _column_info(bind, table_name, column_name)
    if not info:
        return

    if info["udt_name"] == "uuid":
        return

    if info["data_type"] not in {"character varying", "text", "character"}:
        raise RuntimeError(
            f"Tipo no soportado para reconciliar {table_name}.{column_name}: "
            f"{info['data_type']} ({info['udt_name']})"
        )

    _validate_uuid_castable(bind, table_name, column_name)
    q_table = _quote(table_name)
    q_column = _quote(column_name)
    bind.execute(
        sa.text(
            f"""
            ALTER TABLE {q_table}
            ALTER COLUMN {q_column}
            TYPE UUID
            USING {q_column}::uuid
            """
        )
    )


def _ensure_foreign_key(
    bind: sa.Connection,
    table_name: str,
    constraint_name: str,
    local_column: str,
    remote_table: str,
    remote_column: str,
) -> None:
    if not _table_exists(bind, table_name) or not _table_exists(bind, remote_table):
        return

    if _constraint_exists(bind, table_name, constraint_name):
        return

    bind.execute(
        sa.text(
            f"""
            ALTER TABLE {_quote(table_name)}
            ADD CONSTRAINT {_quote(constraint_name)}
            FOREIGN KEY ({_quote(local_column)})
            REFERENCES {_quote(remote_table)} ({_quote(remote_column)})
            """
        )
    )


def _ensure_resenas_table(bind: sa.Connection) -> None:
    if _table_exists(bind, "resenas"):
        return

    op.create_table(
        "resenas",
        sa.Column("id_resena", PgUUID(as_uuid=True), nullable=False),
        sa.Column("id_propiedad", PgUUID(as_uuid=True), nullable=False),
        sa.Column("id_usuario", PgUUID(as_uuid=True), nullable=False),
        sa.Column("nombre_autor", sa.String(), nullable=False),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("calificacion", sa.Integer(), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["id_propiedad"], ["propiedades.id_propiedad"]),
        sa.PrimaryKeyConstraint("id_resena"),
    )


def upgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name != "postgresql":
        return

    _drop_constraint_if_exists(bind, "categorias_habitacion", "categorias_habitacion_id_propiedad_fkey")
    _drop_constraint_if_exists(bind, "resenas", "resenas_id_propiedad_fkey")
    _drop_constraint_if_exists(bind, "inventario", "inventario_id_categoria_fkey")
    _drop_constraint_if_exists(bind, "media", "media_id_categoria_fkey")
    _drop_constraint_if_exists(bind, "categoria_amenidad", "categoria_amenidad_id_categoria_fkey")

    _alter_column_to_uuid(bind, "propiedades", "id_propiedad")
    _alter_column_to_uuid(bind, "categorias_habitacion", "id_propiedad")
    _alter_column_to_uuid(bind, "resenas", "id_propiedad")

    _alter_column_to_uuid(bind, "categorias_habitacion", "id_categoria")
    _alter_column_to_uuid(bind, "inventario", "id_categoria")
    _alter_column_to_uuid(bind, "media", "id_categoria")
    _alter_column_to_uuid(bind, "categoria_amenidad", "id_categoria")

    _ensure_resenas_table(bind)

    _alter_column_to_uuid(bind, "resenas", "id_resena")
    _alter_column_to_uuid(bind, "resenas", "id_usuario")

    _ensure_foreign_key(
        bind,
        "categorias_habitacion",
        "categorias_habitacion_id_propiedad_fkey",
        "id_propiedad",
        "propiedades",
        "id_propiedad",
    )
    _ensure_foreign_key(
        bind,
        "resenas",
        "resenas_id_propiedad_fkey",
        "id_propiedad",
        "propiedades",
        "id_propiedad",
    )
    _ensure_foreign_key(
        bind,
        "inventario",
        "inventario_id_categoria_fkey",
        "id_categoria",
        "categorias_habitacion",
        "id_categoria",
    )
    _ensure_foreign_key(
        bind,
        "media",
        "media_id_categoria_fkey",
        "id_categoria",
        "categorias_habitacion",
        "id_categoria",
    )
    _ensure_foreign_key(
        bind,
        "categoria_amenidad",
        "categoria_amenidad_id_categoria_fkey",
        "id_categoria",
        "categorias_habitacion",
        "id_categoria",
    )


def downgrade() -> None:
    raise RuntimeError(
        "La migracion 002_reconcile_postgres_uuid_schema no soporta downgrade automatico."
    )
