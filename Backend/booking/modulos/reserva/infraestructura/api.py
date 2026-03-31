from flask import Blueprint, request, jsonify
from modulos.reserva.aplicacion.comandos import CrearReservaHold, FormalizarReserva
from modulos.reserva.aplicacion.handlers import CrearReservaHoldHandler, FormalizarReservaHandler
from modulos.reserva.infraestructura.repositorios import RepositorioReservas
from config.uow import UnidadTrabajoHibrida
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
        
        return jsonify({"mensaje": "Reserva creada en estado HOLD (15 min)", "id_reserva": str(id_reserva)}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


@reserva_api.route('/reserva/<id_reserva>/formalizar', methods=['POST'])
def formalizar_reserva(id_reserva):
    try:
        comando = FormalizarReserva(id_reserva=uuid.UUID(id_reserva))
        
        uow = UnidadTrabajoHibrida()
        repositorio = RepositorioReservas()
        handler = FormalizarReservaHandler(repositorio=repositorio, uow=uow)
        
        handler.handle(comando)

        return jsonify({"mensaje": "Reserva formalizada. Iniciando SAGA de confirmación con Hoteles y Pagos"}), 200

    except ValueError as e:
         return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
