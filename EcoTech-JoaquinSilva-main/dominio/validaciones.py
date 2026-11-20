"""Validación de entradas del usuario (lista blanca: solo se acepta lo esperado)."""
import re
import unicodedata

MONEDAS_PERMITIDAS = ("USD", "EUR")

# Letras (con tildes y ñ), espacios, guion y apóstrofe; entre 2 y 60 caracteres.
_PATRON_LUGAR = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ '\-]{1,59}$")
_PATRON_USUARIO = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def validar_ciudad(valor: str) -> str:
    """Devuelve la ciudad limpia o lanza ValueError si tiene caracteres no permitidos."""
    limpio = (valor or "").strip()
    if not _PATRON_LUGAR.match(limpio):
        raise ValueError("Ciudad inválida: solo letras, espacios y guiones (2 a 60 caracteres).")
    return limpio


def _sin_tildes(texto: str) -> str:
    """Pasa a minúsculas y quita tildes, para comparar 'España' con 'espana'."""
    base = unicodedata.normalize("NFD", texto.casefold())
    return "".join(c for c in base if unicodedata.category(c) != "Mn")


# Países donde EcoTech ejecuta proyectos -> moneda de pago (solo las que entrega la API).
PAISES = {
    "Estados Unidos": "USD", "Ecuador": "USD", "Panamá": "USD",
    "España": "EUR", "Alemania": "EUR", "Francia": "EUR", "Italia": "EUR", "Portugal": "EUR",
}
_PAISES_NORMALIZADOS = {_sin_tildes(nombre): (nombre, moneda) for nombre, moneda in PAISES.items()}


def validar_pais(valor: str) -> tuple[str, str]:
    """Acepta solo países de la lista; devuelve (nombre oficial, moneda de pago)."""
    clave = _sin_tildes((valor or "").strip())
    if clave not in _PAISES_NORMALIZADOS:
        raise ValueError("País no permitido. Opciones: " + ", ".join(PAISES) + ".")
    return _PAISES_NORMALIZADOS[clave]


def validar_moneda(valor: str) -> str:
    """Devuelve el código de moneda en mayúsculas si está en la lista permitida."""
    codigo = (valor or "").strip().upper()
    if codigo not in MONEDAS_PERMITIDAS:
        raise ValueError(f"Moneda no permitida. Opciones: {', '.join(MONEDAS_PERMITIDAS)}.")
    return codigo


def validar_usuario(valor: str) -> str:
    """Nombre de usuario: 3 a 30 caracteres entre letras, números y guion bajo."""
    limpio = (valor or "").strip()
    if not _PATRON_USUARIO.match(limpio):
        raise ValueError("Usuario inválido: 3 a 30 caracteres entre letras, números y _.")
    return limpio


def validar_password(valor: str) -> str:
    """Contraseña: mínimo 8 caracteres, con mayúscula, minúscula y número."""
    if not valor or len(valor) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if not (re.search(r"[A-Z]", valor) and re.search(r"[a-z]", valor)
            and re.search(r"\d", valor)):
        raise ValueError("La contraseña debe tener mayúscula, minúscula y número.")
    return valor


def validar_monto(valor: str) -> float:
    """Sueldo en CLP: solo dígitos (se aceptan puntos y espacios como separador), mayor que 0."""
    limpio = (valor or "").replace(".", "").replace(" ", "")
    if not limpio.isdigit():
        raise ValueError("Monto inválido: escribe solo números, por ejemplo 950000.")
    monto = int(limpio)
    if not 0 < monto <= 100_000_000:
        raise ValueError("Monto fuera de rango (1 a 100.000.000).")
    return float(monto)
