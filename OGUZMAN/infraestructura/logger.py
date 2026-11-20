"""Registro de errores técnicos en archivo, sin mostrarlos al usuario ni filtrar llaves."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from infraestructura.config import CLIMA_API_KEY

RUTA_LOGS = Path(__file__).resolve().parent.parent / "logs"


class FiltroSecretos(logging.Filter):
    """Reemplaza la API key por *** si aparece en algún mensaje."""

    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = record.getMessage()
        if CLIMA_API_KEY:
            mensaje = mensaje.replace(CLIMA_API_KEY, "***")
        record.msg = mensaje
        record.args = ()
        return True


def obtener_logger(nombre: str = "ecotech") -> logging.Logger:
    logger = logging.getLogger(nombre)
    if logger.handlers:          # evita duplicar handlers si se llama varias veces
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False     # nada de esto se imprime en pantalla

    RUTA_LOGS.mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        RUTA_LOGS / "ecotech.log", maxBytes=500_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    handler.addFilter(FiltroSecretos())
    logger.addHandler(handler)
    return logger