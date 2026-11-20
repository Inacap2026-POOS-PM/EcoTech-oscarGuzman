"""Validación de entradas del usuario. Se usa lista blanca: solo se acepta lo esperado."""
import re

from dominio.excepciones import ErrorDeValidacion

# Monedas permitidas y su código en la API de mindicador.cl
MONEDAS_PERMITIDAS = {"USD": "dolar", "EUR": "euro"}

_LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
_PATRON_LUGAR = re.compile(rf"[{_LETRAS}]+(?:[ '\-][{_LETRAS}]+)*")
_PATRON_USUARIO = re.compile(r"[A-Za-z0-9_.]{4,20}")
_PATRON_CODIGO_PAIS = re.compile(r"[A-Za-z]{2}")
_PATRON_RUT = re.compile(r"[0-9]{7,8}-[0-9kK]")
_PATRON_ID = re.compile(r"[0-9]{1,9}")

MAX_BYTES_PASSWORD = 72  # límite real de bcrypt


def _limpiar(valor, nombre: str) -> str:
    if not isinstance(valor, str):
        raise ErrorDeValidacion(f"{nombre} no es válido.")
    valor = valor.strip()
    if not valor:
        raise ErrorDeValidacion(f"{nombre} no puede estar vacío.")
    return valor


def validar_lugar(valor, nombre: str = "El lugar") -> str:
    """Ciudad o país: solo letras, espacios, guiones y apóstrofes. Máx. 60 caracteres."""
    valor = _limpiar(valor, nombre)
    if len(valor) > 60 or not _PATRON_LUGAR.fullmatch(valor):
        raise ErrorDeValidacion(f"{nombre} solo puede contener letras y espacios (máx. 60).")
    return valor


def validar_ciudad(ciudad) -> str:
    return validar_lugar(ciudad, "La ciudad")


def validar_pais(pais) -> str:
    return validar_lugar(pais, "El país")


def validar_codigo_pais(codigo) -> str:
    """Código de país de 2 letras (ISO), por ejemplo CL o US."""
    codigo = _limpiar(codigo, "El código de país")
    if not _PATRON_CODIGO_PAIS.fullmatch(codigo):
        raise ErrorDeValidacion("El código de país debe tener 2 letras (ej.: CL, US).")
    return codigo.upper()


def validar_rut(rut) -> str:
    """RUT con guion y dígito verificador, por ejemplo 12345678-9."""
    rut = _limpiar(rut, "El RUT")
    if not _PATRON_RUT.fullmatch(rut):
        raise ErrorDeValidacion("El RUT debe tener el formato 12345678-9.")
    return rut.upper()


def validar_moneda(moneda) -> str:
    moneda = _limpiar(moneda, "La moneda").upper()
    if moneda not in MONEDAS_PERMITIDAS:
        permitidas = ", ".join(MONEDAS_PERMITIDAS)
        raise ErrorDeValidacion(f"Moneda no permitida. Opciones: {permitidas}.")
    return moneda


def validar_monto(monto) -> float:
    try:
        valor = float(str(monto).strip().replace(",", "."))
    except ValueError:
        raise ErrorDeValidacion("El monto debe ser un número.") from None
    if not 0 < valor <= 1_000_000_000:
        raise ErrorDeValidacion("El monto debe ser mayor que 0 y menor a 1.000.000.000.")
    return valor


def validar_nombre_usuario(usuario) -> str:
    usuario = _limpiar(usuario, "El usuario")
    if not _PATRON_USUARIO.fullmatch(usuario):
        raise ErrorDeValidacion("Usuario: 4 a 20 caracteres (letras, números, _ o .).")
    return usuario


def validar_password_login(password) -> str:
    """En el login solo se exige que no venga vacía (no se revela la política de claves)."""
    if not isinstance(password, str) or not password:
        raise ErrorDeValidacion("La contraseña no puede estar vacía.")
    return password


def validar_password_nueva(password) -> str:
    """Al crear un usuario sí se exige una clave mínimamente robusta."""
    password = validar_password_login(password)
    if len(password) < 8:
        raise ErrorDeValidacion("La contraseña debe tener al menos 8 caracteres.")
    if len(password.encode("utf-8")) > MAX_BYTES_PASSWORD:
        raise ErrorDeValidacion("La contraseña es demasiado larga.")
    if not (re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password)):
        raise ErrorDeValidacion("La contraseña debe combinar letras y números.")
    return password

def validar_id_proyecto(valor) -> int:
    """Identificador numérico entero positivo."""
    valor = _limpiar(valor, "El identificador")
    if not _PATRON_ID.fullmatch(valor) or int(valor) == 0:
        raise ErrorDeValidacion("El identificador debe ser un número entero positivo.")
    return int(valor)