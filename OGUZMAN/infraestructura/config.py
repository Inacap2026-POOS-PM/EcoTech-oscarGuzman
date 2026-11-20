"""Configuración centralizada. Es el único lugar que lee las variables de las APIs."""
import os

from dotenv import load_dotenv

load_dotenv()

CLIMA_API_URL = os.environ.get("CLIMA_API_URL", "")
CLIMA_API_KEY = os.environ.get("CLIMA_API_KEY", "")
MONEDAS_API_URL = os.environ.get("MONEDAS_API_URL", "")


def _leer_timeout() -> float:
    """Timeout en segundos; si el valor es inválido, usa 10 por defecto."""
    try:
        valor = float(os.environ.get("API_TIMEOUT", "10"))
    except ValueError:
        return 10.0
    return valor if 0 < valor <= 60 else 10.0


API_TIMEOUT = _leer_timeout()


def clave_clima_configurada() -> bool:
    return bool(CLIMA_API_KEY.strip())