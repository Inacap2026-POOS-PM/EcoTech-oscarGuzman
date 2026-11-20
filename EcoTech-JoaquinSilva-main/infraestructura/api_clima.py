import os

from dotenv import load_dotenv

from infraestructura.cliente_http import get_json
from infraestructura.errores_api import ErrorServicioExterno

load_dotenv()

URL_GEOCODIFICACION = os.environ.get(
    "API_GEO_URL", "https://geocoding-api.open-meteo.com/v1/search")
URL_PRONOSTICO = os.environ.get(
    "API_CLIMA_URL", "https://api.open-meteo.com/v1/forecast")

# Códigos WMO que entrega Open-Meteo -> texto en español.
ESTADOS = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna", 55: "Llovizna intensa",
    61: "Lluvia ligera", 63: "Lluvia", 65: "Lluvia intensa",
    71: "Nieve ligera", 73: "Nieve", 75: "Nieve intensa",
    80: "Chubascos ligeros", 81: "Chubascos", 82: "Chubascos violentos",
    95: "Tormenta", 96: "Tormenta con granizo", 99: "Tormenta fuerte con granizo",
}


def buscar_coordenadas(ciudad: str) -> tuple[float, float, str]:
    """Convierte una ciudad en (latitud, longitud, nombre) usando geocodificación."""
    datos = get_json(URL_GEOCODIFICACION,
                        {"name": ciudad, "count": 1, "language": "es"})
    resultados = datos.get("results")
    if not resultados:
        raise ErrorServicioExterno(f"No se encontró la ciudad '{ciudad}'.")
    lugar = resultados[0]
    try:
        return float(lugar["latitude"]), float(lugar["longitude"]), lugar["name"]
    except (KeyError, TypeError, ValueError) as error:
        raise ErrorServicioExterno("Respuesta de geocodificación incompleta.") from error


def extraer_clima(datos: dict) -> dict:
    """Se queda solo con temperatura, humedad y estado; verifica que sean usables."""
    actual = datos.get("current")
    if not isinstance(actual, dict):
        raise ErrorServicioExterno("La respuesta no trae datos del clima actual.")
    try:
        temperatura = float(actual["temperature_2m"])
        humedad = float(actual["relative_humidity_2m"])
        codigo = int(actual["weather_code"])
    except (KeyError, TypeError, ValueError) as error:
        raise ErrorServicioExterno("Datos del clima incompletos o con formato inválido.") from error
    if not -90 <= temperatura <= 60 or not 0 <= humedad <= 100:
        raise ErrorServicioExterno("Los valores del clima están fuera de rango.")
    return {"temperatura": temperatura, "humedad": humedad,
            "estado": ESTADOS.get(codigo, "Condición desconocida")}


def obtener_clima(ciudad: str) -> dict:
    """Devuelve {'ciudad', 'temperatura', 'humedad', 'estado'} de la ciudad pedida."""
    latitud, longitud, nombre = buscar_coordenadas(ciudad)
    datos = get_json(URL_PRONOSTICO, {
        "latitude": latitud, "longitude": longitud,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
    })
    clima = extraer_clima(datos)
    clima["ciudad"] = nombre
    return clima
