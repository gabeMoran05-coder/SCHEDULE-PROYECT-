CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS catalogo_turnos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO catalogo_turnos (nombre)
VALUES ('Matutino'), ('Vespertino')
ON CONFLICT (nombre) DO NOTHING;
