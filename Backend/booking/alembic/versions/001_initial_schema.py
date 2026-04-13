"""Initial booking schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservas",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("usuario", sa.String(length=40), nullable=False),
        sa.Column("id_categoria", sa.String(length=40), nullable=False),
        sa.Column("codigo_confirmacion_ota", sa.String(length=100), nullable=True),
        sa.Column("codigo_localizador_pms", sa.String(length=100), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("fecha_check_in", sa.String(length=20), nullable=True),
        sa.Column("fecha_check_out", sa.String(length=20), nullable=True),
        sa.Column("ocupacion_adultos", sa.Integer(), nullable=True),
        sa.Column("ocupacion_ninos", sa.Integer(), nullable=True),
        sa.Column("ocupacion_infantes", sa.Integer(), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "saga_definitions",
        sa.Column("id_flujo", sa.String(length=50), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("nombre_descriptivo", sa.String(length=100), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id_flujo", "version"),
    )

    op.create_table(
        "saga_instances",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("id_reserva", sa.String(length=40), nullable=False),
        sa.Column("id_flujo", sa.String(length=50), nullable=False),
        sa.Column("version_ejecucion", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("estado_global", sa.String(length=30), nullable=False),
        sa.Column("paso_actual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("ultima_actualizacion", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "saga_steps_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_flujo", sa.String(length=50), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False),
        sa.Column("comando", sa.String(length=100), nullable=True),
        sa.Column("evento", sa.String(length=100), nullable=True),
        sa.Column("error", sa.String(length=100), nullable=True),
        sa.Column("compensacion", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_flujo", "version"],
            ["saga_definitions.id_flujo", "saga_definitions.version"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "saga_execution_logs",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("id_instancia", sa.String(length=40), nullable=False),
        sa.Column("tipo_mensaje", sa.String(length=30), nullable=False),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("payload_snapshot", sa.JSON(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["id_instancia"], ["saga_instances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    saga_definitions = sa.table(
        "saga_definitions",
        sa.column("id_flujo", sa.String(length=50)),
        sa.column("version", sa.Integer()),
        sa.column("nombre_descriptivo", sa.String(length=100)),
        sa.column("activo", sa.Boolean()),
    )

    saga_steps_definitions = sa.table(
        "saga_steps_definitions",
        sa.column("id", sa.Integer()),
        sa.column("id_flujo", sa.String(length=50)),
        sa.column("version", sa.Integer()),
        sa.column("index", sa.Integer()),
        sa.column("comando", sa.String(length=100)),
        sa.column("evento", sa.String(length=100)),
        sa.column("error", sa.String(length=100)),
        sa.column("compensacion", sa.String(length=100)),
    )

    op.bulk_insert(
        saga_definitions,
        [
            {
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "nombre_descriptivo": "Flujo actual (Cobro -> Bloqueo PMS -> Revision Manual)",
                "activo": True,
            }
        ],
    )

    op.bulk_insert(
        saga_steps_definitions,
        [
            {
                "id": 1,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 0,
                "comando": "CrearReservaLocalCmd",
                "evento": "ReservaCreadaIntegracionEvt",
                "error": "ReservaCreadaFalloEvt",
                "compensacion": "CancelarReservaLocalCmd",
            },
            {
                "id": 2,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 1,
                "comando": "ProcesarPagoCmd",
                "evento": "PagoExitosoEvt",
                "error": "PagoRechazadoEvt",
                "compensacion": "ReversarPagoCmd",
            },
            {
                "id": 3,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 2,
                "comando": "ConfirmarReservaPmsCmd",
                "evento": "ConfirmacionPmsExitosaEvt",
                "error": "ReservaRechazadaPmsEvt",
                "compensacion": "CancelarReservaPmsCmd",
            },
            {
                "id": 4,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 3,
                "comando": "SolicitarAprobacionManualCmd",
                "evento": "ReservaAprobadaManualEvt",
                "error": "ReservaRechazadaManualEvt",
                "compensacion": None,
            },
            {
                "id": 5,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 4,
                "comando": "ConfirmarReservaLocalCmd",
                "evento": "ReservaConfirmadaEvt",
                "error": "FallaActualizacionLocalEvt",
                "compensacion": "CancelarReservaLocalCmd",
            },
            {
                "id": 6,
                "id_flujo": "RESERVA_ESTANDAR",
                "version": 1,
                "index": 5,
                "comando": "MarcarSagaEsperandoVoucher",
                "evento": "VoucherEnviadoEvt",
                "error": "FalloEnvioVoucherEvt",
                "compensacion": "NotificarFalloTecnicoCmd",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("saga_execution_logs")
    op.drop_table("saga_steps_definitions")
    op.drop_table("saga_instances")
    op.drop_table("saga_definitions")
    op.drop_table("reservas")
