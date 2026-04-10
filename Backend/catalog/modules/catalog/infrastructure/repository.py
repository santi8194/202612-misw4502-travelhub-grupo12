from uuid import UUID
from decimal import Decimal
from datetime import date

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import (
	PropiedadModel,
	CategoriaHabitacionModel,
	InventarioModel,
)
from modules.catalog.domain.entities import (
	Propiedad,
	CategoriaHabitacion,
	Inventario,
	Media,
	Amenidad,
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
)


class PropertyRepository:
	"""Repositorio para persistencia del agregado Propiedad."""

	def save(self, propiedad: Propiedad) -> None:
		"""
		Guarda una propiedad en el repositorio.

		Args:
			propiedad: Entidad Propiedad a persistir
		"""
		db: Session = SessionLocal()

		try:
			# Convertir entidad de dominio a modelo de persistencia
			propiedad_model = PropiedadModel(
				id_propiedad=str(propiedad.id_propiedad),
				nombre=propiedad.nombre,
				estrellas=propiedad.estrellas,
				ciudad=propiedad.ubicacion.ciudad,
				pais=propiedad.ubicacion.pais,
				latitud=propiedad.ubicacion.coordenadas.lat,
				longitud=propiedad.ubicacion.coordenadas.lng,
				porcentaje_impuesto=propiedad.porcentaje_impuesto,
			)

			# Guardar categorías de habitación
			for categoria in propiedad.categorias_habitacion:
				categoria_model = CategoriaHabitacionModel(
					id_categoria=categoria.id_categoria,
					id_propiedad=str(propiedad.id_propiedad),
					codigo_mapeo_pms=categoria.codigo_mapeo_pms,
					nombre_comercial=categoria.nombre_comercial,
					descripcion=categoria.descripcion,
					precio_base_monto=categoria.precio_base.monto,
					precio_base_moneda=categoria.precio_base.moneda,
					capacidad_pax=categoria.capacidad_pax,
					dias_anticipacion=categoria.politica_cancelacion.dias_anticipacion,
					porcentaje_penalidad=categoria.politica_cancelacion.porcentaje_penalidad,
				)

				# Guardar inventario
				for inventario in categoria.inventario:
					inventario_model = InventarioModel(
						id_inventario=inventario.id_inventario,
						id_categoria=categoria.id_categoria,
						fecha=inventario.fecha.isoformat(),
						cupos_totales=inventario.cupos_totales,
						cupos_disponibles=inventario.cupos_disponibles,
					)
					categoria_model.inventario.append(inventario_model)

				propiedad_model.categorias_habitacion.append(categoria_model)

			db.merge(propiedad_model)
			db.commit()
		finally:
			db.close()

	def obtain(self, id_propiedad: UUID) -> Propiedad | None:
		"""
		Obtiene una propiedad por su ID.

		Args:
			id_propiedad: UUID de la propiedad

		Returns:
			Propiedad si existe, None en caso contrario
		"""
		db: Session = SessionLocal()

		try:
			propiedad_model = db.query(PropiedadModel).filter(
				PropiedadModel.id_propiedad == str(id_propiedad)
			).first()

			if not propiedad_model:
				return None

			return self._model_to_entity(propiedad_model)
		finally:
			db.close()

	def obtain_all(self) -> list[Propiedad]:
		"""
		Obtiene todas las propiedades.

		Returns:
			Lista de todas las propiedades
		"""
		db: Session = SessionLocal()

		try:
			propiedades_models = db.query(PropiedadModel).all()
			return [self._model_to_entity(model) for model in propiedades_models]
		finally:
			db.close()

	def delete(self, id_propiedad: UUID) -> bool:
		"""
		Elimina una propiedad.

		Args:
			id_propiedad: UUID de la propiedad a eliminar

		Returns:
			True si se eliminó, False si no existe
		"""
		db: Session = SessionLocal()

		try:
			propiedad = db.query(PropiedadModel).filter(
				PropiedadModel.id_propiedad == str(id_propiedad)
			).first()

			if not propiedad:
				return False

			db.delete(propiedad)
			db.commit()
			return True
		finally:
			db.close()

	def _model_to_entity(self, propiedad_model: PropiedadModel) -> Propiedad:
		"""
		Convierte un modelo de persistencia a una entidad de dominio.

		Args:
			propiedad_model: Modelo de persistencia

		Returns:
			Entidad Propiedad del dominio
		"""
		# Reconstruir objeto de valor de ubicación
		coordenadas = Coordenadas(
			lat=propiedad_model.latitud,
			lng=propiedad_model.longitud,
		)
		ubicacion = VODireccion(
			ciudad=propiedad_model.ciudad,
			pais=propiedad_model.pais,
			coordenadas=coordenadas,
		)

		# Reconstruir categorías de habitación
		categorias = []
		for cat_model in propiedad_model.categorias_habitacion:
			# Reconstruir objetos de valor
			precio_base = VODinero(
				monto=cat_model.precio_base_monto,
				moneda=cat_model.precio_base_moneda,
			)
			politica = VORegla(
				dias_anticipacion=cat_model.dias_anticipacion,
				porcentaje_penalidad=cat_model.porcentaje_penalidad,
			)

			# Reconstruir inventario
			inventario_list = [
				Inventario(
					id_inventario=inv_model.id_inventario,
					fecha=date.fromisoformat(inv_model.fecha),
					cupos_totales=inv_model.cupos_totales,
					cupos_disponibles=inv_model.cupos_disponibles,
				)
				for inv_model in cat_model.inventario
			]

			# Crear categoría
			categoria = CategoriaHabitacion(
				id_categoria=cat_model.id_categoria,
				codigo_mapeo_pms=cat_model.codigo_mapeo_pms,
				nombre_comercial=cat_model.nombre_comercial,
				descripcion=cat_model.descripcion,
				precio_base=precio_base,
				capacidad_pax=cat_model.capacidad_pax,
				politica_cancelacion=politica,
				media=[],
				amenidades=[],
				inventario=inventario_list,
			)
			categorias.append(categoria)

		# Crear propiedad
		return Propiedad(
			id_propiedad=UUID(propiedad_model.id_propiedad),
			nombre=propiedad_model.nombre,
			estrellas=propiedad_model.estrellas,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal(str(propiedad_model.porcentaje_impuesto)),
			categorias_habitacion=categorias,
		)
