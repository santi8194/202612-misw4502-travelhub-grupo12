from sqlalchemy import Column, String, Integer, Float, Numeric, ForeignKey, Table, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship
from .database import Base


class PropiedadModel(Base):
	__tablename__ = "propiedades"

	# Clave primaria como UUID nativo de PostgreSQL
	id_propiedad = Column(PgUUID(as_uuid=True), primary_key=True)
	nombre = Column(String, nullable=False)
	estrellas = Column(Integer, nullable=False)
	ciudad = Column(String, nullable=False)
	# Estado o provincia requerido por el servicio Search
	estado_provincia = Column(String, nullable=False)
	pais = Column(String, nullable=False)
	latitud = Column(Float, nullable=False)
	longitud = Column(Float, nullable=False)
	porcentaje_impuesto = Column(Numeric(5, 2), nullable=False)

	categorias_habitacion = relationship(
		"CategoriaHabitacionModel", back_populates="propiedad"
	)
	# Relación con las reseñas de la propiedad
	resenas = relationship(
		"ResenaModel", back_populates="propiedad", cascade="all, delete-orphan"
	)


class CategoriaHabitacionModel(Base):
	__tablename__ = "categorias_habitacion"

	# Clave primaria como UUID nativo de PostgreSQL
	id_categoria = Column(PgUUID(as_uuid=True), primary_key=True)
	# Clave foránea como UUID nativo referenciando propiedades
	id_propiedad = Column(PgUUID(as_uuid=True), ForeignKey("propiedades.id_propiedad"), nullable=False)
	codigo_mapeo_pms = Column(String, nullable=False, unique=True)
	nombre_comercial = Column(String, nullable=False)
	descripcion = Column(String, nullable=False)
	precio_base_monto = Column(Numeric(12, 2), nullable=False)
	precio_base_moneda = Column(String(3), nullable=False)
	precio_base_cargo_servicio = Column(Numeric(12, 2), nullable=False, default=0)
	capacidad_pax = Column(Integer, nullable=False)
	dias_anticipacion = Column(Integer, nullable=False)
	porcentaje_penalidad = Column(Numeric(5, 2), nullable=False)
	# Tarifa diferenciada: fin de semana (nullable = no configurada)
	tarifa_fin_de_semana_monto = Column(Numeric(12, 2), nullable=True)
	tarifa_fin_de_semana_moneda = Column(String(3), nullable=True)
	tarifa_fin_de_semana_cargo_servicio = Column(Numeric(12, 2), nullable=True)
	# Tarifa diferenciada: temporada alta (nullable = no configurada)
	tarifa_temporada_alta_monto = Column(Numeric(12, 2), nullable=True)
	tarifa_temporada_alta_moneda = Column(String(3), nullable=True)
	tarifa_temporada_alta_cargo_servicio = Column(Numeric(12, 2), nullable=True)

	propiedad = relationship("PropiedadModel", back_populates="categorias_habitacion")
	media = relationship("MediaModel", back_populates="categoria", cascade="all, delete-orphan")
	amenidades = relationship(
		"AmenidadModel", secondary="categoria_amenidad", back_populates="categorias"
	)
	inventario = relationship("InventarioModel", back_populates="categoria", cascade="all, delete-orphan")


class MediaModel(Base):
	__tablename__ = "media"

	id_media = Column(String, primary_key=True)
	# FK como UUID nativo apuntando a categorias_habitacion
	id_categoria = Column(PgUUID(as_uuid=True), ForeignKey("categorias_habitacion.id_categoria"), nullable=False)
	url_full = Column(String, nullable=False)
	tipo = Column(String, nullable=False)
	orden = Column(Integer, nullable=False)

	categoria = relationship("CategoriaHabitacionModel", back_populates="media")


class AmenidadModel(Base):
	__tablename__ = "amenidades"

	id_amenidad = Column(String, primary_key=True)
	nombre = Column(String, nullable=False)
	icono = Column(String, nullable=False)

	categorias = relationship(
		"CategoriaHabitacionModel", secondary="categoria_amenidad", back_populates="amenidades"
	)


# Tabla asociativa para relación many-to-many entre categorías y amenidades
categoria_amenidad = Table(
	"categoria_amenidad",
	Base.metadata,
	# FK como UUID nativo
	Column("id_categoria", PgUUID(as_uuid=True), ForeignKey("categorias_habitacion.id_categoria"), primary_key=True),
	Column("id_amenidad", String, ForeignKey("amenidades.id_amenidad"), primary_key=True),
)


class InventarioModel(Base):
	__tablename__ = "inventario"

	id_inventario = Column(String, primary_key=True)
	# FK como UUID nativo apuntando a categorias_habitacion
	id_categoria = Column(PgUUID(as_uuid=True), ForeignKey("categorias_habitacion.id_categoria"), nullable=False)
	fecha = Column(String, nullable=False)
	cupos_totales = Column(Integer, nullable=False)
	cupos_disponibles = Column(Integer, nullable=False)

	categoria = relationship("CategoriaHabitacionModel", back_populates="inventario")


class ResenaModel(Base):
	"""Modelo ORM para reseñas de una propiedad.

	Aplica desnormalización controlada: nombre_autor y avatar_url provienen
	del servicio de Usuarios pero se almacenan aquí para evitar llamadas
	síncronas y garantizar el P95 < 500ms.
	"""
	__tablename__ = "resenas"

	# Clave primaria como UUID nativo de PostgreSQL
	id_resena = Column(PgUUID(as_uuid=True), primary_key=True)
	# FK a la propiedad (la reseña es de la propiedad, no de la categoría)
	id_propiedad = Column(PgUUID(as_uuid=True), ForeignKey("propiedades.id_propiedad"), nullable=False)
	# UUID del usuario autor (sin FK externa: pertenece al microservicio de Usuarios)
	id_usuario = Column(PgUUID(as_uuid=True), nullable=False)
	# Campos del autor desnormalizados
	nombre_autor = Column(String, nullable=False)
	avatar_url = Column(String, nullable=True)
	# Datos de la reseña
	calificacion = Column(Integer, nullable=False)
	comentario = Column(Text, nullable=False)
	# Timestamp con zona horaria para orden cronológico
	fecha_creacion = Column(DateTime(timezone=True), nullable=False)

	propiedad = relationship("PropiedadModel", back_populates="resenas")
