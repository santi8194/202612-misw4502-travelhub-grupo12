from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from modules.catalog.application.commands.create_property import CreateProperty
from modules.catalog.application.commands.register_category_housing import RegisterCategoryHousing
from modules.catalog.application.commands.update_inventory import UpdateInventory
from modules.catalog.application.commands.update_pricing import UpdatePricing
from modules.catalog.application.queries.obtain_property_by_category_id import ObtainPropertyByCategoryId
from modules.catalog.application.queries.obtain_category_by_id import ObtainCategoryById
from modules.catalog.application.queries.obtain_categories_by_property_id import ObtainCategoriesByPropertyId
from modules.catalog.application.queries.obtain_category_view_detail import ObtainCategoryViewDetail

router = APIRouter()
repository = PropertyRepository()
event_bus = EventBus()


@router.get("/health")
def health():
	return {"status": "ok", "service": "catalog"}


# ==================== REQUEST MODELS ====================


class CreatePropertyRequest(BaseModel):
	nombre: str
	estrellas: int
	ciudad: str
	# Estado o provincia requerido por el servicio Search
	estado_provincia: str
	pais: str
	latitud: float
	longitud: float
	porcentaje_impuesto: Decimal


class RegisterCategoryRequest(BaseModel):
	id_propiedad: UUID
	codigo_mapeo_pms: str
	nombre_comercial: str
	descripcion: str
	monto_precio_base: Decimal
	cargo_servicio: Decimal
	moneda_precio_base: str
	capacidad_pax: int
	dias_anticipacion: int
	porcentaje_penalidad: Decimal
	foto_portada_url: str


class UpdateInventoryRequest(BaseModel):
	id_propiedad: UUID
	# UUID de la categoría
	id_categoria: UUID
	id_inventario: str
	fecha: date
	cupos_totales: int
	cupos_disponibles: int


class UpdatePricingRequest(BaseModel):
	tarifa_base_monto: Decimal
	moneda: str
	cargo_servicio: Decimal = Decimal("0")
	tarifa_fin_de_semana_monto: Decimal | None = None
	tarifa_temporada_alta_monto: Decimal | None = None


# ==================== ENDPOINTS ====================


@router.post("/properties")
def crear_propiedad(request: CreatePropertyRequest):
	"""Crea una nueva propiedad."""
	command = CreateProperty(repository, event_bus)
	id_propiedad = uuid4()  # Generar UUID automáticamente
	return command.execute(
		id_propiedad=id_propiedad,
		nombre=request.nombre,
		estrellas=request.estrellas,
		ciudad=request.ciudad,
		estado_provincia=request.estado_provincia,
		pais=request.pais,
		latitud=request.latitud,
		longitud=request.longitud,
		porcentaje_impuesto=request.porcentaje_impuesto,
	)


@router.post("/properties/{id_propiedad}/categories")
def registrar_categoria(id_propiedad: UUID, request: RegisterCategoryRequest):
	"""Registra una nueva categoría de habitación en una propiedad."""
	command = RegisterCategoryHousing(repository, event_bus)
	try:
		result = command.execute(
			id_propiedad=id_propiedad,
			codigo_mapeo_pms=request.codigo_mapeo_pms,
			nombre_comercial=request.nombre_comercial,
			descripcion=request.descripcion,
			monto_precio_base=request.monto_precio_base,
			cargo_servicio=request.cargo_servicio,
			moneda_precio_base=request.moneda_precio_base,
			capacidad_pax=request.capacidad_pax,
			dias_anticipacion=request.dias_anticipacion,
			porcentaje_penalidad=request.porcentaje_penalidad,
			foto_portada_url=request.foto_portada_url,
		)
		if isinstance(result, dict) and result.get("error") == "Property not found":
			return JSONResponse(status_code=404, content=result)
		return result
	except IntegrityError as exc:
		error_text = str(exc.orig).lower() if getattr(exc, "orig", None) else str(exc).lower()
		if "categorias_habitacion.codigo_mapeo_pms" in error_text or "codigo_mapeo_pms" in error_text:
			return JSONResponse(
				status_code=409,
				content={
					"error": "Ya existe una categoria con ese codigo_mapeo_pms. Usa un codigo diferente.",
					"codigo_mapeo_pms": request.codigo_mapeo_pms,
				},
			)
		return JSONResponse(
			status_code=409,
			content={"error": "Conflicto de integridad al registrar la categoria."},
		)
	except Exception as exc:
		return JSONResponse(
			status_code=500,
			content={"error": f"No se pudo registrar la categoria: {str(exc)}"},
		)


@router.get("/properties/{id_propiedad}/categories")
def obtener_categorias_de_propiedad(id_propiedad: UUID):
	"""Obtiene todas las categorías de una propiedad por su ID."""
	command = ObtainCategoriesByPropertyId(repository, event_bus)
	return command.execute(id_propiedad)


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
			"estado_provincia": propiedad.ubicacion.estado_provincia,
			"pais": propiedad.ubicacion.pais,
			"coordenadas": {
				"lat": propiedad.ubicacion.coordenadas.lat,
				"lng": propiedad.ubicacion.coordenadas.lng,
			},
		},
		"porcentaje_impuesto": str(propiedad.porcentaje_impuesto),
		"categorias_habitacion": len(propiedad.categorias_habitacion),
	}


@router.get("/properties/by-category/{id_categoria}")
def obtener_propiedad_por_categoria(id_categoria: UUID):
	"""Obtiene la propiedad asociada a una categoría de habitación."""
	command = ObtainPropertyByCategoryId(repository)
	return command.execute(id_categoria)


@router.get("/categories/{id_categoria}/view-detail")
def obtener_detalle_categoria(id_categoria: UUID):
	"""Retorna el detalle consolidado de la vista de Propiedad para el frontend.

	Incluye datos de la propiedad, categoría solicitada, amenidades, galería
	(máx. 10 elementos con portada primero), rating promedio y las 10 reseñas
	más recientes. Toda la jerarquía se carga en un único viaje a la BD (cero N+1).
	"""
	query = ObtainCategoryViewDetail(repository)
	result = query.execute(id_categoria)
	if "error" in result:
		return JSONResponse(status_code=404, content=result)
	return result


@router.get("/categories/{id_categoria}")
def obtener_categoria_por_id(id_categoria: UUID):
	"""Obtiene una categoría de habitación por su ID."""
	command = ObtainCategoryById(repository)
	return command.execute(id_categoria)


@router.put("/properties/{id_propiedad}/categories/{id_categoria}/pricing")
def actualizar_tarifas(id_propiedad: UUID, id_categoria: UUID, request: UpdatePricingRequest):
	"""Actualiza tarifa base y tarifas diferenciadas (fin de semana, temporada alta)."""
	command = UpdatePricing(repository, event_bus)
	result = command.execute(
		id_propiedad=id_propiedad,
		id_categoria=id_categoria,
		tarifa_base_monto=request.tarifa_base_monto,
		moneda=request.moneda,
		cargo_servicio=request.cargo_servicio,
		tarifa_fin_de_semana_monto=request.tarifa_fin_de_semana_monto,
		tarifa_temporada_alta_monto=request.tarifa_temporada_alta_monto,
	)
	if "error" in result:
		status = 404 if "not found" in result["error"].lower() else 400
		return JSONResponse(status_code=status, content=result)
	return result


@router.get("/properties/{id_propiedad}/categories/{id_categoria}/pricing")
def obtener_tarifas(id_propiedad: UUID, id_categoria: UUID):
	"""Retorna las tarifas actuales de una categoría (base + diferenciadas)."""
	propiedad = repository.obtain(id_propiedad)
	if not propiedad:
		return JSONResponse(status_code=404, content={"error": "Property not found", "id_propiedad": str(id_propiedad)})
	categoria = propiedad.obtener_categoria(id_categoria)
	if not categoria:
		return JSONResponse(status_code=404, content={"error": "Category not found", "id_categoria": str(id_categoria)})

	def _vo(vo):
		if vo is None:
			return None
		return {"monto": str(vo.monto), "moneda": vo.moneda, "cargo_servicio": str(vo.cargo_servicio)}

	return {
		"id_categoria": str(categoria.id_categoria),
		"nombre_comercial": categoria.nombre_comercial,
		"tarifa_base": _vo(categoria.precio_base),
		"tarifa_fin_de_semana": _vo(categoria.tarifa_fin_de_semana),
		"tarifa_temporada_alta": _vo(categoria.tarifa_temporada_alta),
	}


# ==================== TEMPORADAS ====================

class CreateTemporadaRequest(BaseModel):
	nombre: str
	fecha_inicio: str   # "YYYY-MM-DD"
	fecha_fin: str      # "YYYY-MM-DD"
	porcentaje: Decimal


@router.get("/properties/{id_propiedad}/seasons")
def obtener_temporadas(id_propiedad: UUID):
	"""Retorna todas las temporadas de precio de una propiedad."""
	temporadas = repository.get_temporadas(id_propiedad)
	return {"id_propiedad": str(id_propiedad), "temporadas": temporadas}


@router.post("/properties/{id_propiedad}/seasons")
def crear_temporada(id_propiedad: UUID, request: CreateTemporadaRequest):
	"""Crea una nueva temporada de precio para una propiedad."""
	try:
		temporada = repository.save_temporada(
			id_propiedad=id_propiedad,
			id_temporada=uuid4(),
			nombre=request.nombre,
			fecha_inicio=request.fecha_inicio,
			fecha_fin=request.fecha_fin,
			porcentaje=request.porcentaje,
		)
		return temporada
	except Exception as exc:
		return JSONResponse(
			status_code=500,
			content={"error": f"No se pudo crear la temporada: {str(exc)}"},
		)


@router.delete("/properties/{id_propiedad}/seasons/{id_temporada}")
def eliminar_temporada(id_propiedad: UUID, id_temporada: UUID):
	"""Elimina una temporada de precio."""
	deleted = repository.delete_temporada(id_propiedad, id_temporada)
	if not deleted:
		return JSONResponse(status_code=404, content={"error": "Temporada no encontrada"})
	return {"deleted": True, "id_temporada": str(id_temporada)}


@router.get("/properties/{id_propiedad}/categories/{id_categoria}/availability/{fecha}")
def obtener_disponibilidad(id_propiedad: UUID, id_categoria: UUID, fecha: date):
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
				"estado_provincia": p.ubicacion.estado_provincia,
				"pais": p.ubicacion.pais,
				"categorias": len(p.categorias_habitacion),
			}
			for p in propiedades
		],
	}
