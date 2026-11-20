"""Cliente HTTP compartido por las APIs (clima y monedas).

Centraliza: timeout, reintentos, validación de códigos HTTP y mensajes de error
seguros. El detalle técnico va al log; el usuario solo ve mensajes genéricos.
"""

import logging
import os
import time

import requests

TIMEOUT_SEG = 10
REINTENTOS = 2

logging.basicConfig(
    filename="ecotech.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class ErrorDeServicio(Exception):
    """Fallo controlado de un servicio externo. Su mensaje es seguro de mostrar."""


def pedir_json(url: str, params: dict) -> dict:
    """GET con timeout, reintentos y manejo de códigos HTTP. Devuelve el JSON."""
    api_key = os.getenv("ECOTECH_API_KEY")  # opcional; nunca va escrita en el código
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    motivo = "desconocido"

    for intento in range(1, REINTENTOS + 2):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT_SEG)
        except requests.exceptions.Timeout:
            motivo = "timeout"
        except requests.exceptions.ConnectionError:
            motivo = "sin conexión"
        except requests.exceptions.RequestException as e:
            logging.error("Error de requests: %s", type(e).__name__)
            raise ErrorDeServicio("No se pudo completar la consulta al servicio.") from None
        else:
            code = r.status_code
            if code == 200:
                try:
                    return r.json()
                except ValueError:
                    logging.error("JSON inválido desde %s", url)
                    raise ErrorDeServicio("El servicio devolvió datos no válidos.") from None
            if code == 404:
                raise ErrorDeServicio("No se encontró lo solicitado (404).")
            if code in (401, 403):
                logging.error("Acceso denegado (%s) en %s", code, url)
                raise ErrorDeServicio("El servicio rechazó la solicitud (permisos o credenciales).")
            if code == 429:
                motivo = "429 demasiadas solicitudes"
            elif 500 <= code < 600:
                motivo = f"error del servidor {code}"
            else:
                logging.error("HTTP %s en %s", code, url)
                raise ErrorDeServicio(f"El servicio respondió con un código inesperado ({code}).")

        logging.warning("Intento %d/%d falló (%s) en %s", intento, REINTENTOS + 1, motivo, url)
        if intento <= REINTENTOS:
            time.sleep(1.5 * intento)

    raise ErrorDeServicio("El servicio no está disponible por ahora. Intenta más tarde.")
