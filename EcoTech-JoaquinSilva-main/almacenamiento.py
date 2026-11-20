"""Persistencia local de las consultas hechas a servicios externos (SQLite)."""
import json
from datetime import datetime

from infraestructura.conexion import obtener_conexion

_SQL_CREAR = """
    CREATE TABLE IF NOT EXISTS consulta_externa (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo       TEXT NOT NULL,
        detalle    TEXT NOT NULL,
        fecha_hora TEXT NOT NULL
    )
"""


def guardar_consulta(tipo: str, datos: dict) -> None:
    """Guarda una consulta (clima o cambio) con la hora; los datos van como parámetros."""
    with obtener_conexion() as conn:
        conn.execute(_SQL_CREAR)
        conn.execute(
            "INSERT INTO consulta_externa (tipo, detalle, fecha_hora) VALUES (?, ?, ?)",
            (tipo, json.dumps(datos, ensure_ascii=False),
             datetime.now().isoformat(timespec="seconds")),
        )


def listar_consultas(limite: int = 10) -> list[tuple]:
    """Devuelve las últimas consultas como (fecha_hora, tipo, detalle)."""
    with obtener_conexion() as conn:
        conn.execute(_SQL_CREAR)
        return conn.execute(
            "SELECT fecha_hora, tipo, detalle FROM consulta_externa "
            "ORDER BY id DESC LIMIT ?", (int(limite),)).fetchall()
