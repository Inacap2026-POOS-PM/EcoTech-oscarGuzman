"""Seguridad: autenticación con contraseñas cifradas y validación de entradas
(criterio 3.1.2). Usa la conexión SQLite que ya existe en infraestructura.conexion.
"""

import hashlib
import hmac
import logging
import re
import secrets

from infraestructura.conexion import obtener_conexion

PBKDF2_ITERACIONES = 310_000
PATRON_USUARIO = re.compile(r"[A-Za-z0-9_]{4,20}")


class ErrorDeAutenticacion(Exception):
    """Credenciales inválidas o usuario no registrable. Mensaje seguro de mostrar."""


def validar_usuario(usuario: str) -> bool:
    return bool(PATRON_USUARIO.fullmatch(usuario or ""))


def validar_password(password: str) -> list[str]:
    """Devuelve lo que le falta a la contraseña (lista vacía = válida)."""
    faltan = []
    if len(password) < 8:
        faltan.append("mínimo 8 caracteres")
    if not re.search(r"[A-Z]", password):
        faltan.append("una mayúscula")
    if not re.search(r"[a-z]", password):
        faltan.append("una minúscula")
    if not re.search(r"\d", password):
        faltan.append("un número")
    return faltan


def _hashear(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERACIONES)


def _crear_tabla(con) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
               usuario TEXT PRIMARY KEY,
               salt    TEXT NOT NULL,
               hash    TEXT NOT NULL)"""
    )


def hay_usuarios() -> bool:
    with obtener_conexion() as con:
        _crear_tabla(con)
        n = con.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        con.commit()
    return n > 0


def registrar_usuario(usuario: str, password: str) -> None:
    """Guarda el usuario con hash PBKDF2 + salt aleatorio. Nunca guarda la contraseña."""
    if not validar_usuario(usuario):
        raise ErrorDeAutenticacion("Usuario inválido (4-20 letras, números o _).")
    faltan = validar_password(password)
    if faltan:
        raise ErrorDeAutenticacion("Contraseña débil, falta: " + ", ".join(faltan))
    salt = secrets.token_bytes(16)
    with obtener_conexion() as con:
        _crear_tabla(con)
        existe = con.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
        if existe:
            raise ErrorDeAutenticacion("Ese usuario ya existe.")
        # Consulta parametrizada (?) -> evita inyección SQL
        con.execute(
            "INSERT INTO usuarios (usuario, salt, hash) VALUES (?,?,?)",
            (usuario, salt.hex(), _hashear(password, salt).hex()),
        )
        con.commit()
    logging.info("Usuario registrado: %s", usuario)


def autenticar(usuario: str, password: str) -> bool:
    """True si las credenciales son correctas. Mensajes de fallo siempre genéricos."""
    if not usuario or not password:  # no se aceptan valores vacíos
        return False
    fila = None
    if validar_usuario(usuario):
        with obtener_conexion() as con:
            _crear_tabla(con)
            fila = con.execute(
                "SELECT salt, hash FROM usuarios WHERE usuario = ?", (usuario,)
            ).fetchone()
    salt = bytes.fromhex(fila[0]) if fila else b"\x00" * 16
    esperado = bytes.fromhex(fila[1]) if fila else b"\x00" * 32
    # Siempre se calcula el hash y se compara en tiempo constante
    coincide = hmac.compare_digest(_hashear(password, salt), esperado)
    ok = bool(fila) and coincide
    logging.info("Login %s", "correcto: " + usuario if ok else "fallido")
    return ok
