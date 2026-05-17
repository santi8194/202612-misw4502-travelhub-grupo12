from flask import Blueprint, request, jsonify
from modulos.reserva.aplicacion.comandos import CrearReservaHold, FormalizarReserva, ExpirarReserva, CancelarReservaLocalCmd
from modulos.reserva.aplicacion.handlers import CrearReservaHoldHandler, FormalizarReservaHandler, ObtenerReservaPorIdHandler, ObtenerReservasPorUsuarioHandler, ExpirarReservaHandler, CancelarReservaLocalHandler
from modulos.reserva.aplicacion.queries import ObtenerReservasPorUsuario
from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient
from modulos.reserva.infraestructura.auth_client import AuthServiceClient
from modulos.reserva.infraestructura.payment_client import PaymentServiceClient
from modulos.reserva.infraestructura.repositorios import RepositorioAuditoriaCancelacionReserva, RepositorioReservas
from modulos.saga_reservas.dominio.comandos import CancelarReservaPmsCmd
from modulos.saga_reservas.infraestructura.repositorios import RepositorioSagas
from config.uow import UnidadTrabajoHibrida
import datetime
import json
import os
import urllib.error
import urllib.request
import uuid

reserva_api = Blueprint('reserva_api', __name__)

@reserva_api.route('/reserva', methods=['POST'])
def iniciar_reserva_hold():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        campos_obligatorios = ['id_usuario', 'id_categoria', 'fecha_check_in', 'fecha_check_out', 'ocupacion']
        for campo in campos_obligatorios:
            if campo not in data or data[campo] is None:
                return jsonify({"error": f"El campo '{campo}' es obligatorio"}), 400

        id_usuario = uuid.UUID(data.get('id_usuario'))
        id_categoria = uuid.UUID(data.get('id_categoria'))
        fecha_check_in = data.get('fecha_check_in')
        fecha_check_out = data.get('fecha_check_out')
        ocupacion = data.get('ocupacion')

        comando = CrearReservaHold(
            id_usuario=id_usuario,
            id_categoria=id_categoria,
            codigo_confirmacion_ota=data.get('codigo_confirmacion_ota'),
            codigo_localizador_pms=data.get('codigo_localizador_pms'),
            estado=data.get('estado'),
            fecha_check_in=fecha_check_in,
            fecha_check_out=fecha_check_out,
            ocupacion=ocupacion,
            usuario_nombre=data.get('usuario_nombre'),
            usuario_email=data.get('usuario_email')
        )

        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = CrearReservaHoldHandler(repositorio=repositorio, uow=uow)
        
        id_reserva = handler.handle(comando)
        
        return jsonify({"mensaje": "Reserva creada en estado HOLD", "id_reserva": str(id_reserva)}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@reserva_api.route('/reserva/<id_reserva>/formalizar', methods=['POST'])
def formalizar_reserva(id_reserva):
    try:
        data = request.get_json(silent=True) or {}
        intencion_pago = data.get('intencion_pago') or {}
        monto = intencion_pago.get('monto') or data.get('monto')
        moneda = intencion_pago.get('moneda') or data.get('moneda') or 'COP'

        comando = FormalizarReserva(
            id_reserva=uuid.UUID(id_reserva),
            monto=float(monto) if monto is not None else None,
            moneda=moneda
        )
        
        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = FormalizarReservaHandler(repositorio=repositorio, uow=uow)
        
        handler.handle(comando)

        respuesta = {
            "mensaje": "Reserva formalizada. Iniciando SAGA de confirmación con Hoteles y Pagos",
            "id_reserva": id_reserva
        }
        if monto is not None:
            respuesta["pago"] = crear_checkout_pago(id_reserva, float(monto), moneda)

        return jsonify(respuesta), 200

    except ValueError as e:
         return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def crear_checkout_pago(id_reserva: str, monto: float, moneda: str):
    payment_url = os.getenv('PAYMENT_SERVICE_URL', 'http://payment:8002').rstrip('/')
    payload = json.dumps({
        "id_reserva": id_reserva,
        "monto": monto,
        "moneda": moneda
    }).encode('utf-8')

    request_pago = urllib.request.Request(
        f"{payment_url}/payments",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request_pago, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode('utf-8')
        raise RuntimeError(f"No se pudo crear el pago: {detalle}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo conectar con payment: {e.reason}") from e


def _valor_estado_reserva(reserva) -> str | None:
    estado = getattr(reserva, "estado", None)
    return estado.value if hasattr(estado, "value") else estado


def _valor_fecha_iso(fecha) -> str | None:
    return fecha.isoformat() if fecha else None


def _total_huespedes(ocupacion) -> int:
    if not ocupacion:
        return 0

    if isinstance(ocupacion, dict):
        return (
            (ocupacion.get("adultos") or 0)
            + (ocupacion.get("ninos") or 0)
            + (ocupacion.get("infantes") or 0)
        )

    return (
        (getattr(ocupacion, "adultos", 0) or 0)
        + (getattr(ocupacion, "ninos", 0) or 0)
        + (getattr(ocupacion, "infantes", 0) or 0)
    )


def _nested_get(data: dict | None, *keys):
    current = data or {}
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _extraer_politica_cancelacion(category_info: dict) -> dict | None:
    return (
        category_info.get("politica_cancelacion")
        or _nested_get(category_info, "categoria", "politica_cancelacion")
    )


def _extraer_precio_base(category_info: dict) -> dict | None:
    return (
        category_info.get("precio_base")
        or _nested_get(category_info, "categoria", "precio_base")
    )


def _extraer_hotel_name(category_info: dict, property_info: dict) -> str | None:
    return (
        property_info.get("nombre")
        or property_info.get("nombre_comercial")
        or category_info.get("nombre_comercial")
        or _nested_get(category_info, "categoria", "nombre_comercial")
    )


def _extraer_location(property_info: dict) -> str | None:
    ubicacion = property_info.get("ubicacion") if property_info else None
    if isinstance(ubicacion, dict):
        partes = [ubicacion.get("ciudad"), ubicacion.get("pais")]
        return ", ".join([parte for parte in partes if parte]) or None

    partes = [
        property_info.get("ciudad") if property_info else None,
        property_info.get("pais") if property_info else None,
    ]
    return ", ".join([parte for parte in partes if parte]) or None


def _monto_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _policy_type_and_copy(porcentaje_penalidad: float) -> tuple[str, str, str]:
    if porcentaje_penalidad <= 0:
        return (
            "FREE_CANCELLATION",
            "Cancelacion gratuita",
            "La reserva puede cancelarse dentro de la ventana permitida sin penalidad.",
        )
    if porcentaje_penalidad >= 100:
        return (
            "NON_REFUNDABLE",
            "No reembolsable",
            "La reserva puede cancelarse dentro de la ventana permitida sin reembolso.",
        )
    return (
        "PARTIAL_REFUND",
        "Reembolso parcial",
        "La reserva puede cancelarse dentro de la ventana permitida con penalidad parcial.",
    )


def _payment_info_for_preview(payment_info: dict | None, category_info: dict) -> tuple[float, str, bool]:
    payment_info = payment_info or {}
    precio_base = _extraer_precio_base(category_info) or {}

    total_paid = _monto_float(payment_info.get("monto"))
    currency = payment_info.get("moneda") or precio_base.get("moneda") or "COP"
    payment_status = payment_info.get("estado")
    payment_approved = payment_status == "APPROVED"

    return total_paid, currency, payment_approved


def _build_cancellation_preview(reserva, category_info: dict, property_info: dict, payment_info: dict | None) -> dict:
    policy = _extraer_politica_cancelacion(category_info)
    if not policy:
        raise ValueError("No existe politica de cancelacion para la categoria")

    dias_anticipacion = int(policy.get("dias_anticipacion") or 0)
    porcentaje_penalidad = _monto_float(policy.get("porcentaje_penalidad"))
    policy_type, policy_label, policy_description = _policy_type_and_copy(porcentaje_penalidad)

    total_paid, currency, payment_approved = _payment_info_for_preview(payment_info, category_info)
    estado = _valor_estado_reserva(reserva)
    check_in = getattr(reserva, "fecha_check_in", None)
    days_until_check_in = (check_in - datetime.date.today()).days if check_in else None

    can_cancel = True
    non_cancelable_reason = None

    if estado == "CANCELADA":
        can_cancel = False
        non_cancelable_reason = "La reserva ya esta cancelada."
    elif estado == "EXPIRADA":
        can_cancel = False
        non_cancelable_reason = "La reserva ya esta expirada."
    elif estado == "HOLD":
        can_cancel = False
        non_cancelable_reason = "Las reservas en HOLD se liberan por expiracion, no por cancelacion de usuario."
    elif estado == "PENDIENTE":
        can_cancel = False
        non_cancelable_reason = "La reserva pendiente requiere confirmacion antes de evaluar cancelacion."
    elif estado == "CANCELACION_EN_PROCESO":
        can_cancel = False
        non_cancelable_reason = "La reserva ya tiene una cancelacion en proceso."
    elif estado != "CONFIRMADA":
        can_cancel = False
        non_cancelable_reason = "El estado actual de la reserva no permite cancelacion."
    elif not payment_approved:
        can_cancel = False
        non_cancelable_reason = "No existe un pago aprobado confiable para calcular el reembolso."
    elif days_until_check_in is None:
        can_cancel = False
        non_cancelable_reason = "La reserva no tiene fecha de llegada para evaluar la politica."
    elif days_until_check_in < dias_anticipacion:
        can_cancel = False
        non_cancelable_reason = f"La politica requiere al menos {dias_anticipacion} dias de anticipacion para cancelar."

    expected_refund = 0.0
    if can_cancel:
        expected_refund = round(total_paid * (1 - porcentaje_penalidad / 100), 2)

    refund_status = "PENDING" if expected_refund > 0 else "NOT_APPLICABLE"

    return {
        "reservationId": str(reserva.id),
        "reservationNumber": (
            getattr(reserva, "codigo_confirmacion_ota", None)
            or getattr(reserva, "codigo_localizador_pms", None)
            or str(reserva.id)
        ),
        "hotelName": _extraer_hotel_name(category_info, property_info),
        "location": _extraer_location(property_info),
        "checkInDate": _valor_fecha_iso(getattr(reserva, "fecha_check_in", None)),
        "checkOutDate": _valor_fecha_iso(getattr(reserva, "fecha_check_out", None)),
        "guests": _total_huespedes(getattr(reserva, "ocupacion", None)),
        "currentStatus": estado,
        "totalPaid": total_paid,
        "currency": currency,
        "canCancel": can_cancel,
        "nonCancelableReason": non_cancelable_reason,
        "pmsStatus": "PENDING" if estado == "CANCELACION_EN_PROCESO" else None,
        "mensaje": (
            "La cancelacion esta en proceso y espera confirmacion del PMS."
            if estado == "CANCELACION_EN_PROCESO"
            else None
        ),
        "cancellationPolicy": {
            "type": policy_type,
            "label": policy_label,
            "description": policy_description,
            "diasAnticipacion": dias_anticipacion,
            "porcentajePenalidad": porcentaje_penalidad,
        },
        "refund": {
            "paidAmount": total_paid,
            "expectedRefundAmount": expected_refund,
            "refundStatus": refund_status,
            "processingTimeLabel": "5 a 10 dias habiles",
        },
    }


def _build_cancellation_preview_for_reserva(reserva) -> dict:
    id_categoria = str(reserva.id_categoria) if reserva.id_categoria else None
    if not id_categoria:
        raise ValueError("La reserva no tiene categoria asociada para evaluar cancelacion")

    catalog_client = CatalogServiceClient()
    try:
        category_info = catalog_client.get_category_by_id(id_categoria) or {}
        property_info = catalog_client.get_property_by_category_id(id_categoria) or {}
    except ValueError as e:
        raise RuntimeError(str(e)) from e

    payment_client = PaymentServiceClient()
    payment_info = payment_client.get_payment_for_reserva(str(reserva.id))

    return _build_cancellation_preview(
        reserva=reserva,
        category_info=category_info,
        property_info=property_info,
        payment_info=payment_info,
    )


def _cancellation_reference(id_reserva: str) -> str:
    return f"CXL-{id_reserva[:8].upper()}"


def _request_ip_or_none() -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or None
    return request.remote_addr


def _request_user_id_or_none() -> str | None:
    current_user = AuthServiceClient().get_current_user(request.headers.get("Authorization"))
    user_id = current_user.get("id_usuario") if isinstance(current_user, dict) else None
    return str(user_id).strip() if user_id else None


def _ownership_error_for_reserva(reserva):
    request_user_id = _request_user_id_or_none()
    reserva_user_id = (
        str(reserva.usuario.id)
        if getattr(reserva, "usuario", None) and getattr(reserva.usuario, "id", None)
        else None
    )

    if not request_user_id:
        return jsonify({"error": "No se pudo identificar al usuario autenticado"}), 401
    if not reserva_user_id or request_user_id != reserva_user_id:
        return jsonify({"error": "No tiene permiso para acceder a esta reserva"}), 403
    return None


@reserva_api.route('/reserva/<id_reserva>/cancelacion-preview', methods=['GET'])
def obtener_cancelacion_preview(id_reserva):
    try:
        reserva_id = uuid.UUID(id_reserva)
        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = ObtenerReservaPorIdHandler(repositorio=repositorio, uow=uow)
        reserva = handler.handle(reserva_id)

        if not reserva:
            return jsonify({"error": f"No se encontro la reserva con ID: {id_reserva}"}), 404

        ownership_error = _ownership_error_for_reserva(reserva)
        if ownership_error:
            return ownership_error

        preview = _build_cancellation_preview_for_reserva(reserva)

        return jsonify(preview), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/<id_reserva>', methods=['GET'])
def obtener_reserva_por_id(id_reserva):
    try:
        reserva_id = uuid.UUID(id_reserva)
        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = ObtenerReservaPorIdHandler(repositorio=repositorio, uow=uow)
        reserva = handler.handle(reserva_id)

        if not reserva:
            return jsonify({"error": f"No se encontró la reserva con ID: {id_reserva}"}), 404

        return jsonify({
            "id_reserva": str(reserva.id),
            "id_usuario": str(reserva.usuario.id) if reserva.usuario and reserva.usuario.id else None,
            "id_categoria": str(reserva.id_categoria) if reserva.id_categoria else None,
            "codigo_confirmacion_ota": reserva.codigo_confirmacion_ota,
            "codigo_localizador_pms": reserva.codigo_localizador_pms,
            "estado": reserva.estado.value if reserva.estado else None,
            "fecha_check_in": reserva.fecha_check_in.isoformat() if reserva.fecha_check_in else None,
            "fecha_check_out": reserva.fecha_check_out.isoformat() if reserva.fecha_check_out else None,
            "ocupacion": {
                "adultos": reserva.ocupacion.adultos,
                "ninos": reserva.ocupacion.ninos,
                "infantes": reserva.ocupacion.infantes,
            } if reserva.ocupacion else None,
            "fecha_creacion": reserva.fecha_creacion.isoformat() if reserva.fecha_creacion else None,
            "fecha_actualizacion": reserva.fecha_actualizacion.isoformat() if reserva.fecha_actualizacion else None,
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/<id_reserva>/timeline', methods=['GET'])
def obtener_timeline_reserva(id_reserva):
    try:
        # Validamos el formato de UUID para responder 400 consistente con las otras rutas.
        uuid.UUID(id_reserva)

        repositorio_sagas = RepositorioSagas()
        saga = repositorio_sagas.buscar_por_reserva(id_reserva)

        if not saga:
            return jsonify({"error": f"No se encontró timeline para la reserva con ID: {id_reserva}"}), 404

        historial_ordenado = sorted(
            saga.historial or [],
            key=lambda log: log.fecha_registro
        )

        timeline = []
        for log in historial_ordenado:
            tipo_mensaje = log.tipo_mensaje.value if hasattr(log.tipo_mensaje, 'value') else str(log.tipo_mensaje)
            timeline.append({
                "id_log": str(log.id),
                "tipo_mensaje": tipo_mensaje,
                "accion": log.accion,
                "payload": log.payload_snapshot,
                "fecha_registro": log.fecha_registro.isoformat() if log.fecha_registro else None,
            })

        estado_global = saga.estado_global.value if hasattr(saga.estado_global, 'value') else str(saga.estado_global)

        return jsonify({
            "id_reserva": str(saga.id_reserva),
            "id_instancia_saga": str(saga.id),
            "id_flujo": saga.id_flujo,
            "version_ejecucion": saga.version_ejecucion,
            "estado_global": estado_global,
            "paso_actual": saga.paso_actual,
            "total_eventos": len(timeline),
            "timeline": timeline,
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/usuario/<id_usuario>', methods=['GET'])
def obtener_reservas_por_usuario(id_usuario):
    try:
        usuario_uuid = uuid.UUID(id_usuario)
        query = ObtenerReservasPorUsuario(id_usuario=usuario_uuid)
        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = ObtenerReservasPorUsuarioHandler(repositorio=repositorio, uow=uow)
        reservas = handler.handle(query)

        resultado = []
        for reserva in reservas:
            resultado.append({
                "id_reserva": str(reserva.id),
                "id_usuario": str(reserva.usuario.id) if reserva.usuario and reserva.usuario.id else None,
                "id_categoria": str(reserva.id_categoria) if reserva.id_categoria else None,
                "codigo_confirmacion_ota": reserva.codigo_confirmacion_ota,
                "codigo_localizador_pms": reserva.codigo_localizador_pms,
                "estado": reserva.estado.value if reserva.estado else None,
                "fecha_check_in": reserva.fecha_check_in.isoformat() if reserva.fecha_check_in else None,
                "fecha_check_out": reserva.fecha_check_out.isoformat() if reserva.fecha_check_out else None,
                "ocupacion": {
                    "adultos": reserva.ocupacion.adultos,
                    "ninos": reserva.ocupacion.ninos,
                    "infantes": reserva.ocupacion.infantes,
                } if reserva.ocupacion else None,
                "fecha_creacion": reserva.fecha_creacion.isoformat() if reserva.fecha_creacion else None,
                "fecha_actualizacion": reserva.fecha_actualizacion.isoformat() if reserva.fecha_actualizacion else None,
            })

        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/propiedad/<id_propiedad>', methods=['GET'])
def obtener_reservas_por_propiedad(id_propiedad):
    try:
        # Validar UUID de entrada para evitar llamadas innecesarias.
        uuid.UUID(id_propiedad)

        catalog_client = CatalogServiceClient()
        categorias_response = catalog_client.get_categories_by_property_id(id_propiedad) or {}
        categorias = categorias_response.get("categorias") or []

        ids_categoria = [str(cat.get("id_categoria")) for cat in categorias if cat.get("id_categoria")]
        if not ids_categoria:
            return jsonify([]), 200

        categoria_a_nombre = {
            str(cat.get("id_categoria")): cat.get("nombre_comercial")
            for cat in categorias
            if cat.get("id_categoria")
        }

        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        with uow:
            reservas = repositorio.obtener_por_categorias(ids_categoria)

        # Resolver nombres únicos desde authservice (una llamada por usuario único)
        auth_client = AuthServiceClient()
        ids_usuario = list({str(r.usuario.id) for r in reservas if r.usuario and r.usuario.id})
        nombre_por_usuario = {uid: auth_client.get_full_name(uid) for uid in ids_usuario}

        # Resolver pago y total desde payment service
        payment_client = PaymentServiceClient()

        resultado = []

        for reserva in reservas:
            id_categoria = str(reserva.id_categoria) if reserva.id_categoria else None
            if not id_categoria:
                continue

            huespedes = 0
            if reserva.ocupacion:
                huespedes = (
                    (reserva.ocupacion.adultos or 0)
                    + (reserva.ocupacion.ninos or 0)
                    + (reserva.ocupacion.infantes or 0)
                )

            id_usuario = str(reserva.usuario.id) if reserva.usuario and reserva.usuario.id else None
            id_reserva_str = str(reserva.id)

            pago_info = payment_client.get_payment_for_reserva(id_reserva_str)
            pago_estado = pago_info.get("estado") if pago_info else None
            total = pago_info.get("monto") if pago_info else None

            resultado.append({
                "id_reserva": id_reserva_str,
                "id_usuario": id_usuario,
                "nombre_usuario": nombre_por_usuario.get(id_usuario) if id_usuario else None,
                "id_propiedad": id_propiedad,
                "id_categoria": id_categoria,
                "habitacion": categoria_a_nombre.get(id_categoria),
                "estado": reserva.estado.value if reserva.estado else None,
                "fecha_check_in": reserva.fecha_check_in.isoformat() if reserva.fecha_check_in else None,
                "fecha_check_out": reserva.fecha_check_out.isoformat() if reserva.fecha_check_out else None,
                "huespedes": huespedes,
                "pago": pago_estado or "PENDIENTE",
                "total": total,
                "fecha_creacion": reserva.fecha_creacion.isoformat() if reserva.fecha_creacion else None,
                "fecha_actualizacion": reserva.fecha_actualizacion.isoformat() if reserva.fecha_actualizacion else None,
            })

        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/<id_reserva>/expirar', methods=['POST'])
def expirar_reserva(id_reserva):
    try:
        comando = ExpirarReserva(id_reserva=uuid.UUID(id_reserva))

        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = ExpirarReservaHandler(repositorio=repositorio, uow=uow)

        handler.handle(comando)

        return jsonify({"mensaje": "Reserva marcada como EXPIRADA"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reserva_api.route('/reserva/<id_reserva>/cancelar', methods=['POST'])
def cancelar_reserva(id_reserva):
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Debe aceptar los terminos de cancelacion para continuar"}), 400

        accepted_terms = data.get("acceptedTerms")
        if accepted_terms is not True:
            return jsonify({"error": "Debe aceptar los terminos de cancelacion para continuar"}), 400

        reason = data.get("reason")
        reason = reason.strip() if isinstance(reason, str) and reason.strip() else None

        reserva_id = uuid.UUID(id_reserva)
        uow_consulta = UnidadTrabajoHibrida()
        repositorio_consulta = RepositorioReservas()
        handler = ObtenerReservaPorIdHandler(repositorio=repositorio_consulta, uow=uow_consulta)
        reserva = handler.handle(reserva_id)

        if not reserva:
            return jsonify({"error": f"No se encontro la reserva con ID: {id_reserva}"}), 404

        ownership_error = _ownership_error_for_reserva(reserva)
        if ownership_error:
            return ownership_error

        preview = _build_cancellation_preview_for_reserva(reserva)
        if not preview["canCancel"]:
            return jsonify({
                "error": preview["nonCancelableReason"] or "La reserva no se puede cancelar",
                "reservationId": str(reserva.id),
                "reservationStatus": preview["currentStatus"],
                "cancellationReference": _cancellation_reference(str(reserva.id)),
            }), 400

        estado_anterior = preview["currentStatus"]
        cancellation_reference = _cancellation_reference(str(reserva.id))
        refund_amount = preview["refund"]["expectedRefundAmount"]
        refund_status = preview["refund"]["refundStatus"]
        reserva.iniciar_cancelacion()

        uow_actualizacion = UnidadTrabajoHibrida()
        repositorio_actualizacion = RepositorioReservas()
        repositorio_auditoria = RepositorioAuditoriaCancelacionReserva()
        with uow_actualizacion:
            repositorio_actualizacion.actualizar(reserva)
            repositorio_auditoria.registrar_inicio_cancelacion(
                id_reserva=str(reserva.id),
                id_usuario=str(reserva.usuario.id) if getattr(reserva, "usuario", None) and reserva.usuario.id else None,
                ip_origen=_request_ip_or_none(),
                motivo=reason,
                estado_anterior=estado_anterior,
                estado_nuevo="CANCELACION_EN_PROCESO",
                politica_tipo=preview["cancellationPolicy"]["type"],
                dias_anticipacion=preview["cancellationPolicy"]["diasAnticipacion"],
                porcentaje_penalidad=preview["cancellationPolicy"]["porcentajePenalidad"],
                monto_pagado=preview["refund"]["paidAmount"],
                monto_reembolso=refund_amount,
                refund_status=refund_status,
                pms_status="PENDING",
                cancellation_reference=cancellation_reference,
                origen="HU_WEB_11",
            )
            uow_actualizacion.agregar_eventos([
                CancelarReservaPmsCmd(
                    id_reserva=reserva.id,
                    id_categoria=reserva.id_categoria,
                )
            ])
            uow_actualizacion.commit()

        processing_time_label = preview["refund"]["processingTimeLabel"] if refund_amount > 0 else None

        return jsonify({
            "reservationId": str(reserva.id),
            "reservationStatus": "CANCELACION_EN_PROCESO",
            "cancellationReference": cancellation_reference,
            "refundAmount": refund_amount,
            "refundStatus": refund_status,
            "processingTimeLabel": processing_time_label,
            "pmsStatus": "PENDING",
            "mensaje": "Cancelacion iniciada correctamente",
        }), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
