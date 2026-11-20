"""Único punto de salida a internet: timeout, reintentos y errores sin datos sensibles."""
import logging
import time

import requests

from infraestructura.errores_api import ErrorServicioExterno

logger = logging.getLogger("ecotech.api")

TIMEOUT = 10        # segundos por intento
REINTENTOS = 2      # intentos extra si hay timeout o falla de red
ESPERA_BASE = 1     # segundos; crece en cada reintento


def _interpretar(respuesta) -> dict:
    """Decide qué hacer según el código HTTP; solo el 200 entrega datos."""
    codigo = respuesta.status_code
    if codigo == 200:
        try:
            return respuesta.json()
        except ValueError as error:
            logger.error("Respuesta 200 que no es JSON válido")
            raise ErrorServicioExterno("El servicio respondió con un formato inesperado.") from error
    logger.error("El servicio respondió con código HTTP %s", codigo)
    if codigo == 404:
        raise ErrorServicioExterno("El recurso pedido no existe en el servicio externo.")
    if codigo == 429:
        raise ErrorServicioExterno("Demasiadas consultas seguidas. Espera un momento.")
    if codigo >= 500:
        raise ErrorServicioExterno("El servicio externo tiene problemas. Intenta más tarde.")
    raise ErrorServicioExterno("El servicio externo rechazó la consulta.")


def get_json(url: str, parametros: dict | None = None) -> dict:
    """GET con timeout; reintenta si hay timeout o falla de red. Devuelve el JSON como dict."""
    mensaje = ""
    for intento in range(REINTENTOS + 1):
        try:
            respuesta = requests.get(url, params=parametros, timeout=TIMEOUT)
        except requests.exceptions.Timeout:
            logger.warning("Timeout consultando %s (intento %s)", url, intento + 1)
            mensaje = "El servicio externo tardó demasiado en responder."
        except requests.exceptions.ConnectionError:
            logger.warning("Error de conexión con %s (intento %s)", url, intento + 1)
            mensaje = "No hay conexión con el servicio externo. Revisa tu internet."
        except requests.exceptions.RequestException as error:
            logger.error("Error inesperado de requests: %s", type(error).__name__)
            raise ErrorServicioExterno("No se pudo completar la consulta externa.") from error
        else:
            return _interpretar(respuesta)
        if intento < REINTENTOS:
            time.sleep(ESPERA_BASE * (intento + 1))
    raise ErrorServicioExterno(mensaje)
