CREATE TABLE IF NOT EXISTS persona (
    rut       TEXT PRIMARY KEY,
    nombre    TEXT NOT NULL,
    direccion TEXT,
    telefono  TEXT,
    email     TEXT
);


CREATE TABLE IF NOT EXISTS departamento (
    id               TEXT PRIMARY KEY,
    nombre           TEXT NOT NULL,
    gerente_asignado TEXT
);

CREATE TABLE IF NOT EXISTS empleado (
    rut             TEXT PRIMARY KEY,
    fecha_ingreso   DATE NOT NULL,
    sueldo_base     INTEGER NOT NULL,
    departamento_id TEXT,
    FOREIGN KEY (rut) REFERENCES persona(rut),
    FOREIGN KEY (departamento_id) REFERENCES departamento(id)
);

CREATE TABLE IF NOT EXISTS registro_tiempo (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_rut TEXT NOT NULL,
    proyecto_id  INTEGER NOT NULL,
    horas        REAL NOT NULL,
    fecha        DATE NOT NULL,
    descripcion  TEXT,
    FOREIGN KEY (empleado_rut) REFERENCES empleado(rut) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuario (
    nombre     TEXT PRIMARY KEY,
    clave_hash TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS consulta_externa (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo       TEXT NOT NULL,
    detalle    TEXT NOT NULL,
    fecha_hora TEXT NOT NULL
);
