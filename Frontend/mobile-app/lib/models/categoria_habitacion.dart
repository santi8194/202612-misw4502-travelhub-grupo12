class PrecioBase {
  final String monto;
  final String moneda;
  final String cargoServicio;

  const PrecioBase({
    required this.monto,
    required this.moneda,
    required this.cargoServicio,
  });

  factory PrecioBase.fromJson(Map<String, dynamic> json) {
    return PrecioBase(
      monto: json['monto'] as String? ?? '0.00',
      moneda: json['moneda'] as String? ?? '',
      cargoServicio: json['cargo_servicio'] as String? ?? '0.00',
    );
  }
}

class CategoriaPricing {
  final String idCategoria;
  final String nombreComercial;
  final PrecioBase tarifaBase;
  final PrecioBase tarifaFinDeSemana;
  final PrecioBase tarifaTemporadaAlta;

  const CategoriaPricing({
    required this.idCategoria,
    required this.nombreComercial,
    required this.tarifaBase,
    required this.tarifaFinDeSemana,
    required this.tarifaTemporadaAlta,
  });

  factory CategoriaPricing.fromJson(Map<String, dynamic> json) {
    return CategoriaPricing(
      idCategoria: json['id_categoria'] as String? ?? '',
      nombreComercial: json['nombre_comercial'] as String? ?? '',
      tarifaBase: PrecioBase.fromJson(
          json['tarifa_base'] as Map<String, dynamic>? ?? {}),
      tarifaFinDeSemana: PrecioBase.fromJson(
          json['tarifa_fin_de_semana'] as Map<String, dynamic>? ?? {}),
      tarifaTemporadaAlta: PrecioBase.fromJson(
          json['tarifa_temporada_alta'] as Map<String, dynamic>? ?? {}),
    );
  }
}

class PoliticaCancelacion {
  final int diasAnticipacion;
  final String porcentajePenalidad;

  const PoliticaCancelacion({
    required this.diasAnticipacion,
    required this.porcentajePenalidad,
  });

  factory PoliticaCancelacion.fromJson(Map<String, dynamic> json) {
    return PoliticaCancelacion(
      diasAnticipacion: json['dias_anticipacion'] as int? ?? 0,
      porcentajePenalidad: json['porcentaje_penalidad'] as String? ?? '0.00',
    );
  }
}

class CategoriaHabitacion {
  final String idCategoria;
  final String codigoMapeoPms;
  final String nombreComercial;
  final String descripcion;
  final PrecioBase precioBase;
  final String fotoPortadaUrl;
  final int capacidadPax;
  final PoliticaCancelacion politicaCancelacion;

  const CategoriaHabitacion({
    required this.idCategoria,
    required this.codigoMapeoPms,
    required this.nombreComercial,
    required this.descripcion,
    required this.precioBase,
    required this.fotoPortadaUrl,
    required this.capacidadPax,
    required this.politicaCancelacion,
  });

  factory CategoriaHabitacion.fromJson(Map<String, dynamic> json) {
    return CategoriaHabitacion(
      idCategoria: json['id_categoria'] as String? ?? '',
      codigoMapeoPms: json['codigo_mapeo_pms'] as String? ?? '',
      nombreComercial: json['nombre_comercial'] as String? ?? '',
      descripcion: json['descripcion'] as String? ?? '',
      precioBase: PrecioBase.fromJson(
        json['precio_base'] as Map<String, dynamic>? ?? {},
      ),
      fotoPortadaUrl: json['foto_portada_url'] as String? ?? '',
      capacidadPax: json['capacidad_pax'] as int? ?? 0,
      politicaCancelacion: PoliticaCancelacion.fromJson(
        json['politica_cancelacion'] as Map<String, dynamic>? ?? {},
      ),
    );
  }

  String toJson() {
    return '''
    {
      "id_categoria": "$idCategoria",
      "codigo_mapeo_pms": "$codigoMapeoPms",
      "nombre_comercial": "$nombreComercial",
      "descripcion": "$descripcion",
      "precio_base": {
        "monto": "${precioBase.monto}",
        "moneda": "${precioBase.moneda}",
        "cargo_servicio": "${precioBase.cargoServicio}"
      },
      "foto_portada_url": "$fotoPortadaUrl",
      "capacidad_pax": $capacidadPax,
      "politica_cancelacion": {
        "dias_anticipacion": ${politicaCancelacion.diasAnticipacion},
        "porcentaje_penalidad": "${politicaCancelacion.porcentajePenalidad}"
      }
    }
    ''';
  }
}
