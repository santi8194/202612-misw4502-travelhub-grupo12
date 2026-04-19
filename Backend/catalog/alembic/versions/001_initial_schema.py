"""Esquema inicial del catalogo con UUID nativo y estado_provincia."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PgUUID


# Identificadores de revision
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla de propiedades con id_propiedad como UUID nativo
    op.create_table(
        "propiedades",
        sa.Column("id_propiedad", PgUUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("estrellas", sa.Integer(), nullable=False),
        sa.Column("ciudad", sa.String(), nullable=False),
        # Campo requerido por el servicio Search para autocompletado
        sa.Column("estado_provincia", sa.String(), nullable=False),
        sa.Column("pais", sa.String(), nullable=False),
        sa.Column("latitud", sa.Float(), nullable=False),
        sa.Column("longitud", sa.Float(), nullable=False),
        sa.Column("porcentaje_impuesto", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id_propiedad"),
    )

    # Tabla de amenidades (sin cambios de UUID, usa String)
    op.create_table(
        "amenidades",
        sa.Column("id_amenidad", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("icono", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id_amenidad"),
    )

    # Tabla de categorias con id_categoria e id_propiedad como UUID nativo
    op.create_table(
        "categorias_habitacion",
        sa.Column("id_categoria", PgUUID(as_uuid=True), nullable=False),
        sa.Column("id_propiedad", PgUUID(as_uuid=True), nullable=False),
        sa.Column("codigo_mapeo_pms", sa.String(), nullable=False),
        sa.Column("nombre_comercial", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=False),
        sa.Column("precio_base_monto", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("precio_base_moneda", sa.String(length=3), nullable=False),
        sa.Column("precio_base_cargo_servicio", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("capacidad_pax", sa.Integer(), nullable=False),
        sa.Column("dias_anticipacion", sa.Integer(), nullable=False),
        sa.Column("porcentaje_penalidad", sa.Numeric(precision=5, scale=2), nullable=False),
        # FK como UUID nativo apuntando a propiedades
        sa.ForeignKeyConstraint(["id_propiedad"], ["propiedades.id_propiedad"]),
        sa.PrimaryKeyConstraint("id_categoria"),
        sa.UniqueConstraint("codigo_mapeo_pms"),
    )

    # Tabla asociativa category-amenidad: FK de categoria como UUID nativo
    op.create_table(
        "categoria_amenidad",
        sa.Column("id_categoria", PgUUID(as_uuid=True), nullable=False),
        sa.Column("id_amenidad", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["id_amenidad"], ["amenidades.id_amenidad"]),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias_habitacion.id_categoria"]),
        sa.PrimaryKeyConstraint("id_categoria", "id_amenidad"),
    )

    # Tabla de inventario: FK de categoria como UUID nativo
    op.create_table(
        "inventario",
        sa.Column("id_inventario", sa.String(), nullable=False),
        sa.Column("id_categoria", PgUUID(as_uuid=True), nullable=False),
        sa.Column("fecha", sa.String(), nullable=False),
        sa.Column("cupos_totales", sa.Integer(), nullable=False),
        sa.Column("cupos_disponibles", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias_habitacion.id_categoria"]),
        sa.PrimaryKeyConstraint("id_inventario"),
    )

    # Tabla de media: FK de categoria como UUID nativo
    op.create_table(
        "media",
        sa.Column("id_media", sa.String(), nullable=False),
        sa.Column("id_categoria", PgUUID(as_uuid=True), nullable=False),
        sa.Column("url_full", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias_habitacion.id_categoria"]),
        sa.PrimaryKeyConstraint("id_media"),
    )


def downgrade() -> None:
    # Eliminar tablas en orden inverso de dependencias
    op.drop_table("media")
    op.drop_table("inventario")
    op.drop_table("categoria_amenidad")
    op.drop_table("categorias_habitacion")
    op.drop_table("amenidades")
    op.drop_table("propiedades")
