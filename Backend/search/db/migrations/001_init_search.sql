CREATE SCHEMA IF NOT EXISTS search;

CREATE TABLE IF NOT EXISTS search.hospedajes (
    id_propiedad          UUID PRIMARY KEY,
    id_categoria          UUID,
    propiedad_nombre      TEXT,
    categoria_nombre      TEXT,
    imagen_principal_url  TEXT,
    amenidades_destacadas JSONB,
    estrellas             INTEGER,
    rating_promedio       NUMERIC,
    ciudad                TEXT,
    estado_provincia      TEXT,
    pais                  TEXT,
    coordenadas           JSONB,
    capacidad_pax         INTEGER,
    precio_base           NUMERIC,
    moneda                TEXT,
    es_reembolsable       BOOLEAN,
    disponibilidad        JSONB
);

CREATE TABLE IF NOT EXISTS search.destinos (
    id_destino       UUID PRIMARY KEY,
    ciudad           TEXT NOT NULL,
    ciudad_lower     TEXT NOT NULL,
    estado_provincia TEXT,
    pais             TEXT NOT NULL,
    CONSTRAINT unq_destino UNIQUE (ciudad_lower, estado_provincia, pais)
);

CREATE INDEX IF NOT EXISTS idx_destinos_ciudad_prefix
ON search.destinos (ciudad_lower varchar_pattern_ops);
