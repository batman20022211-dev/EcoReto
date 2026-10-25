CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS acciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios (id),
    fecha TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    impacto TEXT NOT NULL
);
