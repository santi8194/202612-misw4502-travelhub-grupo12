from uuid import UUID
from decimal import Decimal
from datetime import date

from sqlalchemy import String, cast
from sqlalchemy.orm import Session, joinedload, selectinload
from .database import IS_SQLITE, SessionLocal
from .models import (
	PropiedadModel,
	CategoriaHabitacionModel,
	AmenidadModel,
	MediaModel,
	InventarioModel,
	ResenaModel,
	TemporadaModel,
	ConfiguracionImpuestosPaisModel,
	categoria_amenidad,
)
from modules.catalog.domain.entities import (
	Propiedad,
	CategoriaHabitacion,
	Inventario,
	Media,
	TipoMedia,
	Amenidad,
	Resena,
	Coordenadas,
	VODireccion,
	VODinero,
	VORegla,
	ConfiguracionImpuestosPais,
)


class PropertyRepository:
	"""Repositorio para persistencia del agregado Propiedad."""

	@staticmethod
	def _apply_property_values(propiedad_model: PropiedadModel, propiedad: Propiedad) -> None:
		propiedad_model.nombre = propiedad.nombre
		propiedad_model.estrellas = propiedad.estrellas
		propiedad_model.ciudad = propiedad.ubicacion.ciudad
		propiedad_model.estado_provincia = propiedad.ubicacion.estado_provincia
		propiedad_model.pais = propiedad.ubicacion.pais
		propiedad_model.latitud = propiedad.ubicacion.coordenadas.lat
		propiedad_model.longitud = propiedad.ubicacion.coordenadas.lng
		propiedad_model.porcentaje_impuesto = propiedad.porcentaje_impuesto

	@staticmethod
	def _apply_category_values(categoria_model: CategoriaHabitacionModel, categoria: CategoriaHabitacion, id_propiedad: UUID) -> None:
		categoria_model.id_propiedad = id_propiedad
		categoria_model.codigo_mapeo_pms = categoria.codigo_mapeo_pms
		categoria_model.nombre_comercial = categoria.nombre_comercial
		categoria_model.descripcion = categoria.descripcion
		categoria_model.precio_base_monto = categoria.precio_base.monto
		categoria_model.precio_base_moneda = categoria.precio_base.moneda
		categoria_model.precio_base_cargo_servicio = categoria.precio_base.cargo_servicio
		categoria_model.capacidad_pax = categoria.capacidad_pax
		categoria_model.dias_anticipacion = categoria.politica_cancelacion.dias_anticipacion
		categoria_model.porcentaje_penalidad = categoria.politica_cancelacion.porcentaje_penalidad
		categoria_model.tarifa_fin_de_semana_monto = categoria.tarifa_fin_de_semana.monto if categoria.tarifa_fin_de_semana else None
		categoria_model.tarifa_fin_de_semana_moneda = categoria.tarifa_fin_de_semana.moneda if categoria.tarifa_fin_de_semana else None
		categoria_model.tarifa_fin_de_semana_cargo_servicio = categoria.tarifa_fin_de_semana.cargo_servicio if categoria.tarifa_fin_de_semana else None
		categoria_model.tarifa_temporada_alta_monto = categoria.tarifa_temporada_alta.monto if categoria.tarifa_temporada_alta else None
		categoria_model.tarifa_temporada_alta_moneda = categoria.tarifa_temporada_alta.moneda if categoria.tarifa_temporada_alta else None
		categoria_model.tarifa_temporada_alta_cargo_servicio = categoria.tarifa_temporada_alta.cargo_servicio if categoria.tarifa_temporada_alta else None

	def _sync_category_children(self, db: Session, categoria_model: CategoriaHabitacionModel, categoria: CategoriaHabitacion) -> None:
		existing_media_by_id = {
			media_model.id_media: media_model
			for media_model in db.query(MediaModel)
			.filter(self._id_filter(MediaModel.id_categoria, categoria.id_categoria))
			.all()
		}
		desired_media_models: list[MediaModel] = []
		desired_media_ids: set[str] = set()
		for media in categoria.media:
			desired_media_ids.add(media.id_media)
			media_model = existing_media_by_id.get(media.id_media)
			if media_model is None:
				media_model = MediaModel(id_media=media.id_media, id_categoria=categoria.id_categoria)
			media_model.url_full = media.url_full
			media_model.tipo = media.tipo.value
			media_model.orden = media.orden
			desired_media_models.append(media_model)
		for media_id, media_model in existing_media_by_id.items():
			if media_id not in desired_media_ids:
				db.delete(media_model)
		categoria_model.media = desired_media_models

		existing_inventory_by_id = {
			inventario_model.id_inventario: inventario_model
			for inventario_model in db.query(InventarioModel)
			.filter(self._id_filter(InventarioModel.id_categoria, categoria.id_categoria))
			.all()
		}
		desired_inventory_models: list[InventarioModel] = []
		desired_inventory_ids: set[str] = set()
		for inventario in categoria.inventario:
			desired_inventory_ids.add(inventario.id_inventario)
			inventario_model = existing_inventory_by_id.get(inventario.id_inventario)
			if inventario_model is None:
				inventario_model = InventarioModel(
					id_inventario=inventario.id_inventario,
					id_categoria=categoria.id_categoria,
				)
			inventario_model.fecha = inventario.fecha.isoformat()
			inventario_model.cupos_totales = inventario.cupos_totales
			inventario_model.cupos_disponibles = inventario.cupos_disponibles
			desired_inventory_models.append(inventario_model)
		for inventario_id, inventario_model in existing_inventory_by_id.items():
			if inventario_id not in desired_inventory_ids:
				db.delete(inventario_model)
		categoria_model.inventario = desired_inventory_models

		if categoria.amenidades:
			amenidad_ids = [amenidad.id_amenidad for amenidad in categoria.amenidades]
			categoria_model.amenidades = (
				db.query(AmenidadModel)
				.filter(AmenidadModel.id_amenidad.in_(amenidad_ids))
				.all()
			)

	@staticmethod
	def _id_filter(column, identifier: UUID | str):
		"""Construye filtro compatible con UUID en SQLite y PostgreSQL."""
		if IS_SQLITE:
			return cast(column, String) == str(identifier)
		return column == identifier

	def _populate_category_relations_sqlite(self, db: Session, categoria_model: CategoriaHabitacionModel) -> None:
		"""Carga relaciones de categoria manualmente en SQLite.

		Con PgUUID(as_uuid=True), algunas relaciones terminan vacías porque
		SQLite persiste los UUID como texto con guiones.
		"""
		categoria_model.media = (
			db.query(MediaModel)
			.filter(self._id_filter(MediaModel.id_categoria, categoria_model.id_categoria))
			.order_by(MediaModel.orden)
			.all()
		)
		categoria_model.inventario = (
			db.query(InventarioModel)
			.filter(self._id_filter(InventarioModel.id_categoria, categoria_model.id_categoria))
			.order_by(InventarioModel.fecha, InventarioModel.id_inventario)
			.all()
		)
		categoria_model.amenidades = (
			db.query(AmenidadModel)
			.join(categoria_amenidad, AmenidadModel.id_amenidad == categoria_amenidad.c.id_amenidad)
			.filter(self._id_filter(categoria_amenidad.c.id_categoria, categoria_model.id_categoria))
			.all()
		)

	@staticmethod
	def _parse_tipo_media(raw_tipo: str) -> TipoMedia:
		"""Convierte valores legacy de BD a TipoMedia del dominio."""
		normalized = (raw_tipo or "").strip().upper()
		legacy_map = {
			"IMAGEN": TipoMedia.IMAGEN_GALERIA,
			"FOTO": TipoMedia.FOTO_PORTADA,
			"PORTADA": TipoMedia.FOTO_PORTADA,
			"GALLERY": TipoMedia.IMAGEN_GALERIA,
		}

		if normalized in legacy_map:
			return legacy_map[normalized]

		try:
			return TipoMedia(normalized)
		except ValueError:
			return TipoMedia.IMAGEN_GALERIA

	def save(self, propiedad: Propiedad) -> None:
		"""
		Guarda una propiedad en el repositorio.

		Args:
			propiedad: Entidad Propiedad a persistir
		"""
		db: Session = SessionLocal()

		try:
			existing_property = (
				db.query(PropiedadModel)
				.filter(self._id_filter(PropiedadModel.id_propiedad, propiedad.id_propiedad))
				.first()
			)

			if existing_property is None:
				propiedad_model = PropiedadModel(id_propiedad=propiedad.id_propiedad)
				db.add(propiedad_model)
			else:
				propiedad_model = existing_property

			self._apply_property_values(propiedad_model, propiedad)

			for categoria in propiedad.categorias_habitacion:
				existing_category = (
					db.query(CategoriaHabitacionModel)
					.filter(self._id_filter(CategoriaHabitacionModel.id_categoria, categoria.id_categoria))
					.first()
				)
				if existing_category is None:
					categoria_model = CategoriaHabitacionModel(id_categoria=categoria.id_categoria)
					db.add(categoria_model)
				else:
					categoria_model = existing_category

				self._apply_category_values(categoria_model, categoria, propiedad.id_propiedad)
				self._sync_category_children(db, categoria_model, categoria)

			db.commit()
		except Exception:
			db.rollback()
			raise
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
			# En SQLite, selectinload sobre UUID(PgUUID) puede no resolver correctamente
			# cuando los IDs están persistidos como texto con guiones.
			if IS_SQLITE:
				propiedad_model = (
					db.query(PropiedadModel)
					.filter(self._id_filter(PropiedadModel.id_propiedad, id_propiedad))
					.first()
				)
				if propiedad_model:
					categorias = (
						db.query(CategoriaHabitacionModel)
						.filter(self._id_filter(CategoriaHabitacionModel.id_propiedad, id_propiedad))
						.all()
					)
					for categoria in categorias:
						self._populate_category_relations_sqlite(db, categoria)
					propiedad_model.categorias_habitacion = categorias
			else:
				# Cargar amenidades con selectinload para evitar N+1 en la relación M2M
				propiedad_model = (
					db.query(PropiedadModel)
					.options(
						selectinload(PropiedadModel.categorias_habitacion)
						.selectinload(CategoriaHabitacionModel.amenidades)
					)
					.filter(self._id_filter(PropiedadModel.id_propiedad, id_propiedad))
					.first()
				)

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
			# Cargar amenidades con selectinload para evitar N+1 en la relación M2M
			propiedades_models = (
				db.query(PropiedadModel)
				.options(
					selectinload(PropiedadModel.categorias_habitacion)
					.selectinload(CategoriaHabitacionModel.amenidades)
				)
				.all()
			)
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
			# Cargar amenidades con selectinload para evitar N+1 en la relación M2M
			categoria_model = (
				db.query(CategoriaHabitacionModel)
				.options(
					selectinload(CategoriaHabitacionModel.amenidades),
					joinedload(CategoriaHabitacionModel.propiedad)
					.selectinload(PropiedadModel.categorias_habitacion)
					.selectinload(CategoriaHabitacionModel.amenidades),
				)
				.filter(self._id_filter(CategoriaHabitacionModel.id_categoria, id_categoria))
				.first()
			)

			if not categoria_model:
				return None

			propiedad_model = categoria_model.propiedad
			if not propiedad_model:
				return None

			if IS_SQLITE:
				for categoria in propiedad_model.categorias_habitacion:
					self._populate_category_relations_sqlite(db, categoria)

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
			# Cargar amenidades con selectinload para evitar N+1 en la relación M2M
			categoria_model = (
				db.query(CategoriaHabitacionModel)
				.options(selectinload(CategoriaHabitacionModel.amenidades))
				.filter(self._id_filter(CategoriaHabitacionModel.id_categoria, id_categoria))
				.first()
			)

			if not categoria_model:
				return None

			if IS_SQLITE:
				self._populate_category_relations_sqlite(db, categoria_model)

			return self._category_model_to_entity(categoria_model)
		finally:
			db.close()

	def obtain_tax_config_by_country(self, pais: str) -> ConfiguracionImpuestosPais | None:
		"""Obtiene la configuración de impuestos de un país por nombre."""
		db: Session = SessionLocal()
		try:
			model = (
				db.query(ConfiguracionImpuestosPaisModel)
				.filter(ConfiguracionImpuestosPaisModel.pais == pais)
				.first()
			)
			if not model:
				return None
			return self._tax_model_to_entity(model)
		finally:
			db.close()

	def obtain_tax_config_by_currency(self, moneda: str) -> ConfiguracionImpuestosPais | None:
		"""Obtiene la configuración de impuestos de un país por código de moneda."""
		db: Session = SessionLocal()
		try:
			model = (
				db.query(ConfiguracionImpuestosPaisModel)
				.filter(ConfiguracionImpuestosPaisModel.moneda == moneda)
				.first()
			)
			if not model:
				return None
			return self._tax_model_to_entity(model)
		finally:
			db.close()

	@staticmethod
	def _tax_model_to_entity(model: ConfiguracionImpuestosPaisModel) -> ConfiguracionImpuestosPais:
		return ConfiguracionImpuestosPais(
			pais=model.pais,
			moneda=model.moneda,
			simbolo_moneda=model.simbolo_moneda,
			locale=model.locale,
			decimales=model.decimales,
			tasa_usd=Decimal(str(model.tasa_usd)),
			impuesto_nombre=model.impuesto_nombre,
			impuesto_tasa=Decimal(str(model.impuesto_tasa)),
		)

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
			# Filtrar por UUID nativo directamente sin convertir a str
			propiedad = db.query(PropiedadModel).filter(
				self._id_filter(PropiedadModel.id_propiedad, id_propiedad)
			).first()

			if not propiedad:
				return False

			db.delete(propiedad)
			db.commit()
			return True
		finally:
			db.close()

	def obtain_view_detail(self, id_categoria: UUID) -> tuple[Propiedad, CategoriaHabitacion] | None:
		"""
		Obtiene la propiedad y la categoría con toda la jerarquía en un solo viaje a BD.

		Estrategia de carga anticipada (cero N+1):
		- CategoriaHabitacion -> media (joinedload)
		- CategoriaHabitacion -> amenidades (selectinload, M2M via tabla asociativa)
		- CategoriaHabitacion -> propiedad -> resenas (joinedload + selectinload)

		Args:
			id_categoria: UUID de la categoría

		Returns:
			Tupla (Propiedad, CategoriaHabitacion) o None si no se encuentra
		"""
		db: Session = SessionLocal()
		try:
			categoria_model = (
				db.query(CategoriaHabitacionModel)
				.options(
					# Cargar la propiedad padre y sus reseñas en la misma query
					joinedload(CategoriaHabitacionModel.propiedad)
					.selectinload(PropiedadModel.resenas),
					# Cargar medios de la categoría (relación 1:N)
					joinedload(CategoriaHabitacionModel.media),
					# Cargar amenidades (relación M2M via tabla asociativa)
					selectinload(CategoriaHabitacionModel.amenidades),
				)
				.filter(self._id_filter(CategoriaHabitacionModel.id_categoria, id_categoria))
				.first()
			)

			if not categoria_model:
				return None

			if IS_SQLITE:
				self._populate_category_relations_sqlite(db, categoria_model)

			# Mapear propiedad con reseñas (mapper especializado)
			propiedad = self._model_to_entity_con_resenas(categoria_model.propiedad)
			# Reutilizar mapper corregido de categoría (ahora incluye amenidades reales)
			categoria = self._category_model_to_entity(categoria_model)

			return propiedad, categoria
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
		# Reconstruir objeto de valor de ubicación con estado_provincia
		coordenadas = Coordenadas(
			lat=propiedad_model.latitud,
			lng=propiedad_model.longitud,
		)
		ubicacion = VODireccion(
			ciudad=propiedad_model.ciudad,
			estado_provincia=propiedad_model.estado_provincia,
			pais=propiedad_model.pais,
			coordenadas=coordenadas,
		)

		# Reconstruir categorías de habitación
		categorias = [self._category_model_to_entity(cat_model) for cat_model in propiedad_model.categorias_habitacion]

		# id_propiedad ya es UUID nativo (PgUUID(as_uuid=True) lo retorna como UUID)
		return Propiedad(
			id_propiedad=propiedad_model.id_propiedad,
			nombre=propiedad_model.nombre,
			estrellas=propiedad_model.estrellas,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal(str(propiedad_model.porcentaje_impuesto)),
			categorias_habitacion=categorias,
		)

	def _category_model_to_entity(self, cat_model: CategoriaHabitacionModel) -> CategoriaHabitacion:
		"""Convierte un modelo de categoría a una entidad de dominio.

		Incluye el mapeo de amenidades reales desde la relación M2M.
		Requiere que las amenidades hayan sido cargadas con eager loading (selectinload).
		"""
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
				tipo=self._parse_tipo_media(media_model.tipo),
				orden=media_model.orden,
			)
			for media_model in sorted(cat_model.media, key=lambda m: m.orden)
		]

		# Mapear amenidades reales desde la relación M2M (antes era amenidades=[])
		amenidades_list = [
			Amenidad(
				id_amenidad=a.id_amenidad,
				nombre=a.nombre,
				icono=a.icono,
			)
			for a in cat_model.amenidades
		]

		# Reconstruir tarifas diferenciadas (nullable)
		tarifa_fin_de_semana = None
		if cat_model.tarifa_fin_de_semana_monto is not None:
			tarifa_fin_de_semana = VODinero(
				monto=cat_model.tarifa_fin_de_semana_monto,
				moneda=cat_model.tarifa_fin_de_semana_moneda,
				cargo_servicio=cat_model.tarifa_fin_de_semana_cargo_servicio or Decimal("0"),
			)

		tarifa_temporada_alta = None
		if cat_model.tarifa_temporada_alta_monto is not None:
			tarifa_temporada_alta = VODinero(
				monto=cat_model.tarifa_temporada_alta_monto,
				moneda=cat_model.tarifa_temporada_alta_moneda,
				cargo_servicio=cat_model.tarifa_temporada_alta_cargo_servicio or Decimal("0"),
			)

		return CategoriaHabitacion(
			# id_categoria ya es UUID nativo (PgUUID(as_uuid=True) lo retorna como UUID)
			id_categoria=cat_model.id_categoria,
			codigo_mapeo_pms=cat_model.codigo_mapeo_pms,
			nombre_comercial=cat_model.nombre_comercial,
			descripcion=cat_model.descripcion,
			precio_base=precio_base,
			capacidad_pax=cat_model.capacidad_pax,
			politica_cancelacion=politica,
			media=media_list,
			amenidades=amenidades_list,
			inventario=inventario_list,
			tarifa_fin_de_semana=tarifa_fin_de_semana,
			tarifa_temporada_alta=tarifa_temporada_alta,
		)

	def _model_to_entity_con_resenas(self, propiedad_model: PropiedadModel) -> Propiedad:
		"""Convierte modelo de propiedad a entidad incluyendo reseñas.

		Mapper especializado para el endpoint view-detail donde las reseñas
		se cargan con eager loading. No incluye categorias_habitacion para
		evitar trabajo innecesario en esa vista.
		"""
		# Reconstruir objeto de valor de ubicación
		coordenadas = Coordenadas(
			lat=propiedad_model.latitud,
			lng=propiedad_model.longitud,
		)
		ubicacion = VODireccion(
			ciudad=propiedad_model.ciudad,
			estado_provincia=propiedad_model.estado_provincia,
			pais=propiedad_model.pais,
			coordenadas=coordenadas,
		)
		# Mapear reseñas desde el modelo ORM (cargadas con eager loading)
		resenas = [
			Resena(
				id_resena=r.id_resena,
				id_propiedad=r.id_propiedad,
				id_usuario=r.id_usuario,
				nombre_autor=r.nombre_autor,
				avatar_url=r.avatar_url,
				calificacion=r.calificacion,
				comentario=r.comentario,
				fecha_creacion=r.fecha_creacion,
			)
			for r in propiedad_model.resenas
		]
		return Propiedad(
			id_propiedad=propiedad_model.id_propiedad,
			nombre=propiedad_model.nombre,
			estrellas=propiedad_model.estrellas,
			ubicacion=ubicacion,
			porcentaje_impuesto=Decimal(str(propiedad_model.porcentaje_impuesto)),
			# No necesitamos todas las categorías en view-detail, solo la solicitada
			categorias_habitacion=[],
			resenas=resenas,
		)

	# ==================== TEMPORADAS ====================

	def get_temporadas(self, id_propiedad: UUID) -> list[dict]:
		db: Session = SessionLocal()
		try:
			rows = (
				db.query(TemporadaModel)
				.filter(self._id_filter(TemporadaModel.id_propiedad, id_propiedad))
				.order_by(TemporadaModel.fecha_inicio)
				.all()
			)
			return [
				{
					"id_temporada": str(r.id_temporada),
					"nombre": r.nombre,
					"fecha_inicio": r.fecha_inicio,
					"fecha_fin": r.fecha_fin,
					"porcentaje": float(r.porcentaje),
				}
				for r in rows
			]
		finally:
			db.close()

	def save_temporada(self, id_propiedad: UUID, id_temporada: UUID, nombre: str, fecha_inicio: str, fecha_fin: str, porcentaje: Decimal) -> dict:
		db: Session = SessionLocal()
		try:
			model = TemporadaModel(
				id_temporada=id_temporada,
				id_propiedad=id_propiedad,
				nombre=nombre,
				fecha_inicio=fecha_inicio,
				fecha_fin=fecha_fin,
				porcentaje=porcentaje,
			)
			db.add(model)
			db.commit()
			return {
				"id_temporada": str(id_temporada),
				"nombre": nombre,
				"fecha_inicio": fecha_inicio,
				"fecha_fin": fecha_fin,
				"porcentaje": float(porcentaje),
			}
		except Exception:
			db.rollback()
			raise
		finally:
			db.close()

	def delete_temporada(self, id_propiedad: UUID, id_temporada: UUID) -> bool:
		db: Session = SessionLocal()
		try:
			row = (
				db.query(TemporadaModel)
				.filter(
					self._id_filter(TemporadaModel.id_temporada, id_temporada),
					self._id_filter(TemporadaModel.id_propiedad, id_propiedad),
				)
				.first()
			)
			if not row:
				return False
			db.delete(row)
			db.commit()
			return True
		finally:
			db.close()
