from sqlalchemy import Column, String, Integer, Float, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base


class PropiedadModel(Base):
	__tablename__ = "propiedades"

	id_propiedad = Column(String, primary_key=True)
	nombre = Column(String, nullable=False)
	estrellas = Column(Integer, nullable=False)
	ciudad = Column(String, nullable=False)
	pais = Column(String, nullable=False)
	latitud = Column(Float, nullable=False)
	longitud = Column(Float, nullable=False)
	porcentaje_impuesto = Column(Numeric(5, 2), nullable=False)

	categorias_habitacion = relationship(
		"CategoriaHabitacionModel", back_populates="propiedad"
	)


class CategoriaHabitacionModel(Base):
	__tablename__ = "categorias_habitacion"

	id_categoria = Column(String, primary_key=True)
	id_propiedad = Column(String, ForeignKey("propiedades.id_propiedad"), nullable=False)
	codigo_mapeo_pms = Column(String, nullable=False, unique=True)
	nombre_comercial = Column(String, nullable=False)
	descripcion = Column(String, nullable=False)
	precio_base_monto = Column(Numeric(12, 2), nullable=False)
	precio_base_moneda = Column(String(3), nullable=False)
	capacidad_pax = Column(Integer, nullable=False)
	dias_anticipacion = Column(Integer, nullable=False)
	porcentaje_penalidad = Column(Numeric(5, 2), nullable=False)

	propiedad = relationship("PropiedadModel", back_populates="categorias_habitacion")
	media = relationship("MediaModel", back_populates="categoria", cascade="all, delete-orphan")
	amenidades = relationship(
		"AmenidadModel", secondary="categoria_amenidad", back_populates="categorias"
	)
	inventario = relationship("InventarioModel", back_populates="categoria", cascade="all, delete-orphan")


class MediaModel(Base):
	__tablename__ = "media"

	id_media = Column(String, primary_key=True)
	id_categoria = Column(String, ForeignKey("categorias_habitacion.id_categoria"), nullable=False)
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


# Tabla asociativa para relación many-to-many
categoria_amenidad = Table(
	"categoria_amenidad",
	Base.metadata,
	Column("id_categoria", String, ForeignKey("categorias_habitacion.id_categoria"), primary_key=True),
	Column("id_amenidad", String, ForeignKey("amenidades.id_amenidad"), primary_key=True),
)


class InventarioModel(Base):
	__tablename__ = "inventario"

	id_inventario = Column(String, primary_key=True)
	id_categoria = Column(String, ForeignKey("categorias_habitacion.id_categoria"), nullable=False)
	fecha = Column(String, nullable=False)
	cupos_totales = Column(Integer, nullable=False)
	cupos_disponibles = Column(Integer, nullable=False)

	categoria = relationship("CategoriaHabitacionModel", back_populates="inventario")
