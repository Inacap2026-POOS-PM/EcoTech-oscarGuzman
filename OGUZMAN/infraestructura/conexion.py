import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

from infraestructura.logger import obtener_logger

load_dotenv()
_logger = obtener_logger()


class ErrorDePersistencia(Exception):
    """Base de todos los errores de la capa de datos."""


class ErrorDeConexion(ErrorDePersistencia):
    """No se pudo configurar, abrir o usar la base de datos."""


class ErrorDeIntegridad(ErrorDePersistencia):
    """Se violó una restricción: UNIQUE, FOREIGN KEY, NOT NULL."""


@contextmanager
def obtener_conexion():
    """Entrega una conexión a la base; confirma al salir y cierra siempre."""
    ruta = os.environ.get("DB_NOMBRE")
    if not ruta:
        raise ErrorDeConexion("Falta la variable DB_NOMBRE. ¿Copiaste el .env.example?")
    conn = None
    try:
        conn = sqlite3.connect(ruta)
        conn.execute("PRAGMA foreign_keys = ON")   # SQLite las ignora si no se activan
        yield conn
        conn.commit()
    except sqlite3.IntegrityError as e:   # primero: es subclase de sqlite3.Error
        if conn:
            conn.rollback()
        _logger.warning("Violación de integridad: %s", e)   # el detalle queda solo en el log
        raise ErrorDeIntegridad(
            "No se pudo guardar: el dato ya existe o incumple una restricción."
        ) from None
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        _logger.error("Error de base de datos (%s): %s", type(e).__name__, e)
        raise ErrorDeConexion("No se pudo operar sobre la base de datos.") from None
    finally:
        if conn:
            conn.close()