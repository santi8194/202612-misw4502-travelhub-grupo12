from uuid import UUID
from decimal import Decimal
from datetime import date

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import (
	PropiedadModel,
	CategoriaHabitacionModel,
	MediaModel,
	InventarioModel,
)
from modules.catalog.domain.entities import (
	Propiedad,
	CategoriaHabitacion,
	Inventario,
	Media,
	TipoMedia,
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
					precio_base_cargo_servicio=categoria.precio_base.cargo_servicio,
					capacidad_pax=categoria.capacidad_pax,
					dias_anticipacion=categoria.politica_cancelacion.dias_anticipacion,
					porcentaje_penalidad=categoria.politica_cancelacion.porcentaje_penalidad,
				)

				for media in categoria.media:
					media_model = MediaModel(
						id_media=media.id_media,
						id_categoria=categoria.id_categoria,
						url_full=media.url_full,
						tipo=media.tipo.value,
						orden=media.orden,
					)
					categoria_model.media.append(media_model)

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

	def obtain_by_category_id(self, id_categoria: str) -> Propiedad | None:
		"""
		Obtiene la propiedad asociada a una categoría de habitación.

		Args:
			id_categoria: ID de categoría

		Returns:
			Propiedad asociada si existe, None en caso contrario
		"""
		db: Session = SessionLocal()

		try:
			categoria_model = db.query(CategoriaHabitacionModel).filter(
				CategoriaHabitacionModel.id_categoria == id_categoria
			).first()

			if not categoria_model:
				return None

			propiedad_model = categoria_model.propiedad
			if not propiedad_model:
				return None

			return self._model_to_entity(propiedad_model)
		finally:
			db.close()

	def obtain_category_by_id(self, id_categoria: str) -> CategoriaHabitacion | None:
		"""
		Obtiene una categoría de habitación por su ID.

		Args:
			id_categoria: ID de categoría

		Returns:
			Categoría si existe, None en caso contrario
		"""
		db: Session = SessionLocal()

		try:
			categoria_model = db.query(CategoriaHabitacionModel).filter(
				CategoriaHabitacionModel.id_categoria == id_categoria
			).first()

			if not categoria_model:
				return None

			return self._category_model_to_entity(categoria_model)
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
		categorias = [self._category_model_to_entity(cat_model) for cat_model in propiedad_model.categorias_habitacion]

		# Crear propiedad
		return Propiedad(
			id_propiedad=UUID(propiedad_model.id_propiedad),
			nombre=propiedad_model.nombre,
			estrellas=propiedad_model.estrellas,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal(str(propiedad_model.porcentaje_impuesto)),
			categorias_habitacion=categorias,
		)

	def _category_model_to_entity(self, cat_model: CategoriaHabitacionModel) -> CategoriaHabitacion:
		precio_base = VODinero(
			monto=cat_model.precio_base_monto,
			moneda=cat_model.precio_base_moneda,
			cargo_servicio=cat_model.precio_base_cargo_servicio,
		)
		politica = VORegla(
			dias_anticipacion=cat_model.dias_anticipacion,
			porcentaje_penalidad=cat_model.porcentaje_penalidad,
		)

		inventario_list = [
			Inventario(
				id_inventario=inv_model.id_inventario,
				fecha=date.fromisoformat(inv_model.fecha),
				cupos_totales=inv_model.cupos_totales,
				cupos_disponibles=inv_model.cupos_disponibles,
			)
			for inv_model in cat_model.inventario
		]

		media_list = [
			Media(
				id_media=media_model.id_media,
				url_full=media_model.url_full,
				tipo=TipoMedia(media_model.tipo),
				orden=media_model.orden,
			)
			for media_model in sorted(cat_model.media, key=lambda m: m.orden)
		]

		return CategoriaHabitacion(
			id_categoria=cat_model.id_categoria,
			codigo_mapeo_pms=cat_model.codigo_mapeo_pms,
			nombre_comercial=cat_model.nombre_comercial,
			descripcion=cat_model.descripcion,
			precio_base=precio_base,
			capacidad_pax=cat_model.capacidad_pax,
			politica_cancelacion=politica,
			media=media_list,
			amenidades=[],
			inventario=inventario_list,
		)
