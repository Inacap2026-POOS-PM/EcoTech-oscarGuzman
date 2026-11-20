"""Hash de contraseñas con bcrypt. Nunca se guarda una contraseña en texto plano."""
import bcrypt


def hashear_password(password: str) -> str:
    """Devuelve el hash (el salt aleatorio va incluido dentro del propio hash)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Compara la clave ingresada con el hash guardado. Ante cualquier problema, False."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_guardado.encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        return False