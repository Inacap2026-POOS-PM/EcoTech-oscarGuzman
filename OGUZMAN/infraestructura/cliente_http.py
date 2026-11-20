""""Cliente HTTP común: timeout, reintentos, códigos de estado y errores controlados."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dominio.excepciones import ErrorDeServicioExterno
from infraestructura.config import API_TIMEOUT
from infraestructura.logger import obtener_logger

_logger = obtener_logger()

_MENSAJES_HTTP = {
    401: "El servicio rechazó las credenciales configuradas.",
    403: "Acceso denegado por el servicio externo.",
    404: "No se encontró lo solicitado en el servicio externo.",
    429: "Se superó el límite de consultas. Intente más tarde.",
}


def _crear_sesion() -> requests.Session:
    """Sesión que reintenta fallos de conexión y errores 5xx (nunca el 429)."""
    reintentos = Retry(
        total=2,
        backoff_factor=1,                       # espera 1 s, luego 2 s
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,                  # al agotarse, devuelve la respuesta
    )
    sesion = requests.Session()
    sesion.mount("https://", HTTPAdapter(max_retries=reintentos))
    return sesion


_sesion = _crear_sesion()


def obtener_json(url: str, servicio: str, params: dict | None = None) -> dict:
    """GET con timeout y reintentos. Devuelve el JSON o lanza ErrorDeServicioExterno."""
    try:
        respuesta = _sesion.get(url, params=params, timeout=API_TIMEOUT)
    except requests.exceptions.Timeout:
        _logger.warning("%s: tiempo de espera agotado", servicio)
        raise ErrorDeServicioExterno("El servicio tardó demasiado en responder.") from None
    except requests.exceptions.ConnectionError as e:
        # SSLError es un tipo de ConnectionError; solo se registra el tipo, no el texto.
        _logger.warning("%s: error de conexión (%s)", servicio, type(e).__name__)
        raise ErrorDeServicioExterno("No se pudo conectar con el servicio externo.") from None
    except requests.exceptions.RequestException as e:
        # Solo el tipo de error: el texto de la excepción puede incluir la URL con la llave.
        _logger.error("%s: fallo de solicitud (%s)", servicio, type(e).__name__)
        raise ErrorDeServicioExterno("No se pudo completar la consulta externa.") from None

    codigo = respuesta.status_code
    if codigo != 200:
        _logger.warning("%s: respuesta HTTP %s", servicio, codigo)
        if codigo >= 500:
            mensaje = "El servicio externo no está disponible por ahora."
        else:
            mensaje = _MENSAJES_HTTP.get(codigo, "El servicio devolvió una respuesta inesperada.")
        raise ErrorDeServicioExterno(mensaje)

    try:
        datos = respuesta.json()
    except ValueError:
        _logger.warning("%s: la respuesta no es JSON", servicio)
        raise ErrorDeServicioExterno("La respuesta del servicio no tiene el formato esperado.") from None
    if not isinstance(datos, dict):
        raise ErrorDeServicioExterno("La respuesta del servicio no tiene el formato esperado.")
    return datos