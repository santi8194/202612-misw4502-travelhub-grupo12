from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_inventory import UpdateInventory
from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from datetime import date
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
	id_categoria = data["id_categoria"]
	codigo_mapeo_pms = data["codigo_mapeo_pms"]
	nombre_comercial = data["nombre_comercial"]
	descripcion = data["descripcion"]
	monto_precio_base = Decimal(str(data["monto_precio_base"]))
	moneda_precio_base = data["moneda_precio_base"]
	capacidad_pax = data["capacidad_pax"]
	dias_anticipacion = data["dias_anticipacion"]
	porcentaje_penalidad = Decimal(str(data["porcentaje_penalidad"]))

	print(
		f"[CATALOG] Command received: RegisterCategoryHousing {nombre_comercial} in property {id_propiedad}"
	)

	repository = PropertyRepository()
	event_bus = EventBus()

	use_case = RegisterCategoryHousing(repository, event_bus)

	result = use_case.execute(
		id_propiedad=id_propiedad,
		id_categoria=id_categoria,
		codigo_mapeo_pms=codigo_mapeo_pms,
		nombre_comercial=nombre_comercial,
		descripcion=descripcion,
		monto_precio_base=monto_precio_base,
		moneda_precio_base=moneda_precio_base,
		capacidad_pax=capacidad_pax,
		dias_anticipacion=dias_anticipacion,
		porcentaje_penalidad=porcentaje_penalidad,
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
