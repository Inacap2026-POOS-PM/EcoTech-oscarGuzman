"""Consumo de la API de tipo de cambio (Frankfurter, sin llave) - criterio 3.1.1."""

import re
from decimal import Decimal, InvalidOperation

from infraestructura.http_cliente import ErrorDeServicio, pedir_json

CAMBIO_URL = "https://api.frankfurter.dev/v1/latest"
PATRON_MONEDA = re.compile(r"[A-Z]{3}")


def sanear_moneda(texto: str) -> str | None:
    """Valida un código de moneda de 3 letras (USD, CLP...). None si no es válido."""
    texto = texto.strip().upper()
    return texto if PATRON_MONEDA.fullmatch(texto) else None


def sanear_monto(texto) -> Decimal | None:
    """Convierte a Decimal. Rechaza vacíos, NaN, negativos, cero y valores enormes."""
    try:
        monto = Decimal(str(texto).strip().replace(",", "."))
    except InvalidOperation:
        return None
    if not monto.is_finite() or monto <= 0 or monto > Decimal("1000000000"):
        return None
    return monto


def obtener_tipo_cambio(base: str, destino: str) -> Decimal:
    """Cuántas unidades de `destino` vale 1 unidad de `base`."""
    base, destino = sanear_moneda(base), sanear_moneda(destino)
    if base is None or destino is None:
        raise ErrorDeServicio("Código de moneda inválido (3 letras, ej. USD, EUR, CLP).")
    if base == destino:
        raise ErrorDeServicio("Las monedas deben ser distintas.")

    datos = pedir_json(CAMBIO_URL, {"base": base, "symbols": destino})
    try:
        return Decimal(str(datos["rates"][destino]))
    except (KeyError, TypeError, InvalidOperation):
        raise ErrorDeServicio(
            f"No hay tipo de cambio disponible para {base}→{destino}."
        ) from None


def convertir_pago(monto, base: str, destino: str) -> tuple[Decimal, Decimal]:
    """Devuelve (tasa, monto convertido) para calcular el pago en moneda local."""
    monto_ok = sanear_monto(monto)
    if monto_ok is None:
        raise ErrorDeServicio("Monto inválido (número mayor que 0).")
    tasa = obtener_tipo_cambio(base, destino)
    return tasa, (monto_ok * tasa).quantize(Decimal("0.01"))
