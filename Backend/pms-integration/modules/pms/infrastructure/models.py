from sqlalchemy import Column, String, Integer, Index, DateTime
from datetime import datetime
from .database import Base

class ReservationModel(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True)
    reservation_id = Column(String)
    id_categoria = Column(String)
    id_usuario = Column(String)
    hotel_code = Column(String)
    room_type_code = Column(String)
    state = Column(String)
    hotel_id = Column(String)
    fecha_check_in = Column(String)
    fecha_check_out = Column(String)
    version = Column(Integer, nullable=False, default=1)

    # -----------------------------------------------------------------------
    # Protección contra overbooking con historial completo:
    #
    # Índice único PARCIAL (solo PostgreSQL):
    #   - Solo aplica cuando state != 'CANCELLED'.
    #   - Permite N registros CANCELLED para (room_id, fecha_reserva),
    #     preservando el historial de cancelaciones.
    #   - Bloquea atómicamente un segundo registro ACTIVO para la misma
    #     habitación y fecha, eliminando el race condition TOCTOU.
    #   - En SQLite (entorno local / fallback), este índice es ignorado.
    #     La validación recae en obtain_active_by_room_and_date().
    # -----------------------------------------------------------------------
    __table_args__ = (
        Index(
            'idx_categoria_range_active',
            'id_categoria',
            'fecha_check_in',
            'fecha_check_out',
            unique=True,
            postgresql_where=(Column('state') != 'CANCELLED')
        ),
    )

    # Bloqueo Optimista: protege actualizaciones concurrentes al mismo registro.
    # SQLAlchemy lanzará StaleDataError si la versión no coincide en un UPDATE.
    __mapper_args__ = {
        "version_id_col": version
    }


class SyncCursorModel(Base):
    """
    Modelo para almacenar el cursor de sincronización del polling.
    
    Registra el último timestamp procesado para cada proveedor PMS,
    permitiendo consultar solo cambios incrementales.
    """
    __tablename__ = "sync_cursors"
    
    provider_name = Column(String, primary_key=True)
    last_sync_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)