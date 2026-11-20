-- Proyectos con ubicación, para consultar el clima del lugar donde se ejecutan.
CREATE TABLE IF NOT EXISTS proyecto (
    id     INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT,
    pais   TEXT CHECK (pais IS NULL OR length(pais) = 2)
);