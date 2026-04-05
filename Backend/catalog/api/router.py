from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_inventory import UpdateInventory

router = APIRouter()
repository = PropertyRepository()
event_bus = EventBus()


# ==================== REQUEST MODELS ====================


class CreatePropertyRequest(BaseModel):
	nombre: str
	estrellas: int
	ciudad: str
	pais: str
	latitud: float
	longitud: float
	porcentaje_impuesto: Decimal


class RegisterCategoryRequest(BaseModel):
	id_propiedad: UUID
	id_categoria: str
	codigo_mapeo_pms: str
	nombre_comercial: str
	descripcion: str
	monto_precio_base: Decimal
	moneda_precio_base: str
	capacidad_pax: int
	dias_anticipacion: int
	porcentaje_penalidad: Decimal


class UpdateInventoryRequest(BaseModel):
	id_propiedad: UUID
	id_categoria: str
	id_inventario: str
	fecha: date
	cupos_totales: int
	cupos_disponibles: int


# ==================== ENDPOINTS ====================


@router.post("/properties")
def crear_propiedad(request: CreatePropertyRequest):
	"""Crea una nueva propiedad."""
	command = CreateProperty(repository, event_bus)
	id_propiedad = UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")  # Generar UUID en el cliente
	return command.execute(
		id_propiedad=id_propiedad,
		nombre=request.nombre,
		estrellas=request.estrellas,
		ciudad=request.ciudad,
		pais=request.pais,
		latitud=request.latitud,
		longitud=request.longitud,
		porcentaje_impuesto=request.porcentaje_impuesto,
	)


@router.post("/properties/{id_propiedad}/categories")
def registrar_categoria(id_propiedad: UUID, request: RegisterCategoryRequest):
	"""Registra una nueva categoría de habitación en una propiedad."""
	command = RegisterCategoryHousing(repository, event_bus)
	return command.execute(
		id_propiedad=id_propiedad,
		id_categoria=request.id_categoria,
		codigo_mapeo_pms=request.codigo_mapeo_pms,
		nombre_comercial=request.nombre_comercial,
		descripcion=request.descripcion,
		monto_precio_base=request.monto_precio_base,
		moneda_precio_base=request.moneda_precio_base,
		capacidad_pax=request.capacidad_pax,
		dias_anticipacion=request.dias_anticipacion,
		porcentaje_penalidad=request.porcentaje_penalidad,
	)


@router.put("/properties/{id_propiedad}/categories/{id_categoria}/inventory")
def actualizar_inventario(request: UpdateInventoryRequest):
	"""Actualiza el inventario de una categoría de habitación."""
	command = UpdateInventory(repository, event_bus)
	return command.execute(
		id_propiedad=request.id_propiedad,
		id_categoria=request.id_categoria,
		id_inventario=request.id_inventario,
		fecha=request.fecha,
		cupos_totales=request.cupos_totales,
		cupos_disponibles=request.cupos_disponibles,
	)


@router.get("/properties/{id_propiedad}")
def obtener_propiedad(id_propiedad: UUID):
	"""Obtiene una propiedad por su ID."""
	propiedad = repository.obtain(id_propiedad)
	if not propiedad:
		return {"error": "Property not found", "id_propiedad": str(id_propiedad)}

	return {
		"id_propiedad": str(propiedad.id_propiedad),
		"nombre": propiedad.nombre,
		"estrellas": propiedad.estrellas,
		"ubicacion": {
			"ciudad": propiedad.ubicacion.ciudad,
			"pais": propiedad.ubicacion.pais,
			"coordenadas": {
				"lat": propiedad.ubicacion.coordenadas.lat,
				"lng": propiedad.ubicacion.coordenadas.lng,
			},
		},
		"porcentaje_impuesto": str(propiedad.porcentaje_impuesto),
		"categorias_habitacion": len(propiedad.categorias_habitacion),
	}


@router.get("/properties/{id_propiedad}/categories/{id_categoria}/availability/{fecha}")
def obtener_disponibilidad(id_propiedad: UUID, id_categoria: str, fecha: date):
	"""Obtiene la disponibilidad de una categoría en una fecha específica."""
	propiedad = repository.obtain(id_propiedad)
	if not propiedad:
		return {"error": "Property not found", "id_propiedad": str(id_propiedad)}

	inventario = propiedad.disponibilidad_para(id_categoria, fecha)
	if not inventario:
		return {
			"error": "No inventory found",
			"id_propiedad": str(id_propiedad),
			"id_categoria": id_categoria,
			"fecha": fecha.isoformat(),
		}

	return {
		"id_propiedad": str(id_propiedad),
		"id_categoria": id_categoria,
		"fecha": fecha.isoformat(),
		"cupos_totales": inventario.cupos_totales,
		"cupos_disponibles": inventario.cupos_disponibles,
	}


@router.get("/properties")
def obtener_propiedades():
	"""Obtiene todas las propiedades."""
	propiedades = repository.obtain_all()
	return {
		"total": len(propiedades),
		"propiedades": [
			{
				"id_propiedad": str(p.id_propiedad),
				"nombre": p.nombre,
				"estrellas": p.estrellas,
				"ciudad": p.ubicacion.ciudad,
				"pais": p.ubicacion.pais,
				"categorias": len(p.categorias_habitacion),
			}
			for p in propiedades
		],
	}
