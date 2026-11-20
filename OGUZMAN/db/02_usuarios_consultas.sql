-- Usuarios del sistema (Unidad 3): las contraseñas se guardan solo como hash bcrypt.
CREATE TABLE IF NOT EXISTS usuarios (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario    TEXT    NOT NULL UNIQUE,
    hash_password     TEXT    NOT NULL,
    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
    bloqueado         INTEGER NOT NULL DEFAULT 0 CHECK (bloqueado IN (0, 1)),
    fecha_creacion    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Historial local de consultas a servicios externos (persistencia de datos).
CREATE TABLE IF NOT EXISTS consultas_externas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo       TEXT    NOT NULL CHECK (tipo IN ('clima', 'moneda')),
    parametro  TEXT    NOT NULL,
    resultado  TEXT    NOT NULL,
    usuario_id INTEGER NOT NULL,
    fecha      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);