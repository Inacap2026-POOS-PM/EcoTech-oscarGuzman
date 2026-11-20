"""Autenticación: contraseñas con hash + sal, y control de intentos de login."""
import hashlib
import hmac
import os

from dominio.validaciones import validar_password, validar_usuario
from infraestructura.conexion import obtener_conexion

MAX_INTENTOS = 3

_SQL_CREAR_TABLA = """
    CREATE TABLE IF NOT EXISTS usuario (
        nombre        TEXT PRIMARY KEY,
        clave_hash    TEXT NOT NULL
    )
"""

# Parámetros de scrypt (función diseñada para hashear contraseñas, es lenta a propósito).
_N, _R, _P = 2 ** 14, 8, 1


class ErrorDeAutenticacion(Exception):
    """Credenciales vacías o incorrectas."""


def hashear_password(password: str) -> str:
    """Devuelve 'sal$hash' en hexadecimal. La sal es aleatoria: dos iguales dan hash distinto."""
    sal = os.urandom(16)
    derivado = hashlib.scrypt(password.encode("utf-8"), salt=sal, n=_N, r=_R, p=_P)
    return f"{sal.hex()}${derivado.hex()}"


def verificar_password(password: str, almacenado: str) -> bool:
    """Recalcula el hash con la misma sal y lo compara en tiempo constante."""
    try:
        sal_hex, hash_hex = almacenado.split("$")
        derivado = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(sal_hex),
                                  n=_N, r=_R, p=_P)
        return hmac.compare_digest(derivado, bytes.fromhex(hash_hex))
    except ValueError:   # formato corrupto en la base
        return False


def preparar_tabla() -> None:
    """Crea la tabla de usuarios si no existe."""
    with obtener_conexion() as conn:
        conn.execute(_SQL_CREAR_TABLA)


def hay_usuarios() -> bool:
    """Indica si ya existe al menos un usuario registrado."""
    preparar_tabla()
    with obtener_conexion() as conn:
        return conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] > 0


def registrar_usuario(nombre: str, password: str) -> None:
    """Valida y guarda el usuario con su contraseña ya hasheada (nunca en texto plano)."""
    nombre = validar_usuario(nombre)
    validar_password(password)
    preparar_tabla()
    with obtener_conexion() as conn:
        conn.execute("INSERT INTO usuario (nombre, clave_hash) VALUES (?, ?)",
                     (nombre, hashear_password(password)))


def autenticar(nombre: str, password: str) -> bool:
    """Devuelve True si las credenciales son correctas; ErrorDeAutenticacion si están vacías."""
    if not nombre or not nombre.strip() or not password:
        raise ErrorDeAutenticacion("Debes ingresar usuario y contraseña.")
    preparar_tabla()
    with obtener_conexion() as conn:
        fila = conn.execute("SELECT clave_hash FROM usuario WHERE nombre = ?",
                            (nombre.strip(),)).fetchone()
    # Si el usuario no existe igual se hace un hash, para que no se note la diferencia de tiempo.
    almacenado = fila[0] if fila else hashear_password("relleno")
    correcto = verificar_password(password, almacenado)
    return bool(fila) and correcto
