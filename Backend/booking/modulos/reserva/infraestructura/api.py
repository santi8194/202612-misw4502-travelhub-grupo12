from flask import Blueprint, request, jsonify
from modulos.reserva.aplicacion.comandos import CrearReservaHold, FormalizarReserva, ExpirarReserva
from modulos.reserva.aplicacion.handlers import CrearReservaHoldHandler, FormalizarReservaHandler, ObtenerReservaPorIdHandler, ObtenerReservasPorUsuarioHandler, ExpirarReservaHandler
from modulos.reserva.aplicacion.queries import ObtenerReservasPorUsuario
from modulos.reserva.infraestructura.catalog_client import CatalogServiceClient
from modulos.reserva.infraestructura.repositorios import RepositorioReservas
from config.uow import UnidadTrabajoHibrida
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

            resultado.append({
                "id_reserva": str(reserva.id),
                "id_usuario": str(reserva.usuario.id) if reserva.usuario and reserva.usuario.id else None,
                "id_propiedad": id_propiedad,
                "id_categoria": id_categoria,
                "habitacion": categoria_a_nombre.get(id_categoria),
                "estado": reserva.estado.value if reserva.estado else None,
                "fecha_check_in": reserva.fecha_check_in.isoformat() if reserva.fecha_check_in else None,
                "fecha_check_out": reserva.fecha_check_out.isoformat() if reserva.fecha_check_out else None,
                "huespedes": huespedes,
                "pago": "PENDIENTE",
                "total": None,
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
