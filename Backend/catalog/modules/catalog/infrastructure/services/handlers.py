from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_inventory import UpdateInventory
from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.infrastructure.database import SessionLocal
from modules.catalog.infrastructure.models import InventarioModel, CategoriaHabitacionModel
from modules.catalog.domain.events import InventarioActualizado
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


def handle_create_property(data):
	"""Maneja el comando para crear una propiedad."""
	id_propiedad = UUID(data["id_propiedad"])
	nombre = data["nombre"]
	estrellas = data["estrellas"]
	ciudad = data["ciudad"]
	pais = data["pais"]
	latitud = data["latitud"]
	longitud = data["longitud"]
	porcentaje_impuesto = Decimal(str(data["porcentaje_impuesto"]))

	print(
		f"[CATALOG] Command received: CreateProperty for {nombre} in {ciudad}, {pais}"
	)

	repository = PropertyRepository()
	event_bus = EventBus()

	use_case = CreateProperty(repository, event_bus)

	result = use_case.execute(
		id_propiedad=id_propiedad,
		nombre=nombre,
		estrellas=estrellas,
		ciudad=ciudad,
		pais=pais,
		latitud=latitud,
		longitud=longitud,
		porcentaje_impuesto=porcentaje_impuesto,
	)

	print("[CATALOG] Result:", result)
	return result


def handle_register_category_housing(data):
	"""Maneja el comando para registrar una categoría de habitación."""
	id_propiedad = UUID(data["id_propiedad"])
	codigo_mapeo_pms = data["codigo_mapeo_pms"]
	nombre_comercial = data["nombre_comercial"]
	descripcion = data["descripcion"]
	monto_precio_base = Decimal(str(data["monto_precio_base"]))
	cargo_servicio = Decimal(str(data["cargo_servicio"]))
	moneda_precio_base = data["moneda_precio_base"]
	capacidad_pax = data["capacidad_pax"]
	dias_anticipacion = data["dias_anticipacion"]
	porcentaje_penalidad = Decimal(str(data["porcentaje_penalidad"]))
	foto_portada_url = data["foto_portada_url"]

	print(
		f"[CATALOG] Command received: RegisterCategoryHousing {nombre_comercial} in property {id_propiedad}"
	)

	repository = PropertyRepository()
	event_bus = EventBus()

	use_case = RegisterCategoryHousing(repository, event_bus)

	result = use_case.execute(
		id_propiedad=id_propiedad,
		codigo_mapeo_pms=codigo_mapeo_pms,
		nombre_comercial=nombre_comercial,
		descripcion=descripcion,
		monto_precio_base=monto_precio_base,
		cargo_servicio=cargo_servicio,
		moneda_precio_base=moneda_precio_base,
		capacidad_pax=capacidad_pax,
		dias_anticipacion=dias_anticipacion,
		porcentaje_penalidad=porcentaje_penalidad,
		foto_portada_url=foto_portada_url,
	)

	print("[CATALOG] Result:", result)
	return result


def handle_update_inventory(data):
	"""Maneja el comando para actualizar el inventario."""
	id_propiedad = UUID(data["id_propiedad"])
	id_categoria = data["id_categoria"]
	id_inventario = data["id_inventario"]
	fecha = date.fromisoformat(data["fecha"])
	cupos_totales = data["cupos_totales"]
	cupos_disponibles = data["cupos_disponibles"]

	print(
		f"[CATALOG] Command received: UpdateInventory for category {id_categoria} on {fecha}"
	)

	repository = PropertyRepository()
	event_bus = EventBus()

	use_case = UpdateInventory(repository, event_bus)

	result = use_case.execute(
		id_propiedad=id_propiedad,
		id_categoria=id_categoria,
		id_inventario=id_inventario,
		fecha=fecha,
		cupos_totales=cupos_totales,
		cupos_disponibles=cupos_disponibles,
	)

	print("[CATALOG] Result:", result)
	return result


def handle_pms_inventory_updated(data):
	"""
	Maneja el evento PMSInventoryUpdated del PMS.
	
	Resuelve el UUID de la categoría a partir del codigo_mapeo_pms
	(formato hotel_code:room_type_code) consultando la base de datos local.
	Implementa idempotencia por timestamp y control de concurrencia
	con SELECT FOR UPDATE para evitar race conditions.
	
	Args:
		data: Payload del evento PMSInventoryUpdated
	"""
	try:
		codigo_mapeo_pms = data["codigo_mapeo_pms"]
		fecha_str = data["fecha"]
		cupos_totales = data["cupos_totales"]
		cupos_disponibles = data["cupos_disponibles"]
		event_timestamp_str = data["event_timestamp"]

		fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
		event_timestamp = datetime.fromisoformat(event_timestamp_str.replace('Z', '+00:00'))

		print(f"[CATALOG] Procesando PMSInventoryUpdated: {codigo_mapeo_pms} @ {fecha} -> {cupos_disponibles} cupos")

		db = SessionLocal()

		categoria_row = db.query(CategoriaHabitacionModel).filter_by(
			codigo_mapeo_pms=codigo_mapeo_pms
		).first()

		if not categoria_row:
			print(f"[CATALOG] Categoría no encontrada para codigo_mapeo_pms: {codigo_mapeo_pms}. Evento ignorado.")
			db.close()
			return

		id_categoria = categoria_row.id_categoria
		
		try:
			inventario = db.query(InventarioModel).filter_by(
				id_categoria=id_categoria,
				fecha=fecha.isoformat()
			).with_for_update().first()
			
			if not inventario:
				print(f"[CATALOG] Inventario no encontrado para {id_categoria} @ {fecha}. Creando nuevo registro.")
				
				# Se usa cupos_totales del evento PMS solo al crear registros nuevos
				inventario = InventarioModel(
					id_inventario=f"{id_categoria}-{fecha.isoformat()}",
					id_categoria=id_categoria,
					fecha=fecha.isoformat(),
					cupos_totales=cupos_totales,
					cupos_disponibles=cupos_disponibles,
					last_pms_update_at=event_timestamp
				)
				db.add(inventario)
				db.commit()
				
				_publish_inventario_actualizado(inventario)
				
				print(f"[CATALOG] Inventario creado: {inventario.id_inventario}")
				return
			
			if inventario.last_pms_update_at and event_timestamp <= inventario.last_pms_update_at:
				print(f"[CATALOG] Evento descartado (timestamp viejo): {event_timestamp} <= {inventario.last_pms_update_at}")
				db.rollback()
				return
			
			inventario.cupos_disponibles = cupos_disponibles
			inventario.last_pms_update_at = event_timestamp
			
			db.commit()
			
			_publish_inventario_actualizado(inventario)
			
			print(f"[CATALOG] Inventario actualizado: {inventario.id_inventario} -> {cupos_disponibles} cupos")
			
		except Exception as e:
			db.rollback()
			print(f"[CATALOG] Error actualizando inventario: {e}")
			raise
		finally:
			db.close()
			
	except KeyError as e:
		raise ValueError(f"Campo requerido faltante en evento: {e}")
	except Exception as e:
		print(f"[CATALOG] Error procesando PMSInventoryUpdated: {e}")
		raise


def _publish_inventario_actualizado(inventario: InventarioModel):
	"""
	Publica evento InventarioActualizado hacia Search.
	
	Args:
		inventario: Modelo de inventario actualizado
	"""
	try:
		event_bus = EventBus()
		
		event = InventarioActualizado(
			id_propiedad=str(inventario.categoria.id_propiedad) if inventario.categoria else "unknown",
			id_categoria=str(inventario.id_categoria),
			id_inventario=inventario.id_inventario,
			fecha=inventario.fecha,
			cupos_totales=inventario.cupos_totales,
			cupos_disponibles=inventario.cupos_disponibles
		)
		
		event_bus.publish_event(
			routing_key=event.routing_key,
			event_type=event.type,
			payload=event.to_dict()
		)
		
		print(f"[CATALOG] Evento InventarioActualizado publicado: {inventario.id_inventario}")
		
	except Exception as e:
		print(f"[CATALOG] Error publicando InventarioActualizado: {e}")
