-- Migración: cambiar PK de hospedajes de id_propiedad a id_categoria
-- Esto permite que una propiedad tenga múltiples categorías de habitación sin duplicados.

ALTER TABLE search.hospedajes DROP CONSTRAINT hospedajes_pkey;

ALTER TABLE search.hospedajes ALTER COLUMN id_categoria SET NOT NULL;
ALTER TABLE search.hospedajes ADD CONSTRAINT hospedajes_pkey PRIMARY KEY (id_categoria);

CREATE INDEX IF NOT EXISTS idx_hospedajes_id_propiedad ON search.hospedajes (id_propiedad);
