"""Consumo de la API de clima (Open-Meteo, sin llave) - criterio 3.1.1."""

import logging
import re

from infraestructura.http_cliente import ErrorDeServicio, pedir_json

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
CLIMA_URL = "https://api.open-meteo.com/v1/forecast"

# Lista blanca: letras (con tildes/ñ), espacios, guion y apóstrofe; 2 a 60 caracteres
PATRON_CIUDAD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ '\-]{1,59}")


def sanear_ciudad(texto: str) -> str | None:
    """Limpia espacios y valida la ciudad. Devuelve None si no es válida."""
    texto = " ".join(texto.strip().split())
    return texto if PATRON_CIUDAD.fullmatch(texto) else None


def descripcion_clima(codigo) -> str:
    """Traduce el código WMO de Open-Meteo a texto."""
    if codigo == 0:
        return "Despejado"
    if codigo in (1, 2, 3):
        return "Parcialmente nublado"
    if codigo in (45, 48):
        return "Niebla"
    if codigo in range(51, 68) or codigo in range(80, 83):
        return "Lluvia"
    if codigo in range(71, 78) or codigo in (85, 86):
        return "Nieve"
    if codigo in (95, 96, 99):
        return "Tormenta"
    return "Sin información"


def obtener_clima(ciudad: str) -> dict:
    """Devuelve temperatura, humedad, viento y estado del tiempo de una ciudad."""
    ciudad_ok = sanear_ciudad(ciudad)
    if ciudad_ok is None:
        raise ErrorDeServicio("Ciudad inválida: usa solo letras, espacios o guiones.")

    geo = pedir_json(
        GEO_URL, {"name": ciudad_ok, "count": 1, "language": "es", "format": "json"}
    )
    resultados = geo.get("results")
    if not resultados:
        raise ErrorDeServicio(f"No se encontró la ciudad '{ciudad_ok}'.")
    lugar = resultados[0]

    datos = pedir_json(
        CLIMA_URL,
        {
            "latitude": lugar["latitude"],
            "longitude": lugar["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        },
    )
    try:
        actual = datos["current"]
        return {
            "ciudad": lugar.get("name", ciudad_ok),
            "pais": lugar.get("country", ""),
            "temperatura": actual["temperature_2m"],
            "humedad": actual["relative_humidity_2m"],
            "viento": actual["wind_speed_10m"],
            "estado": descripcion_clima(actual.get("weather_code")),
        }
    except (KeyError, TypeError):
        logging.error("Respuesta de clima con formato inesperado")
        raise ErrorDeServicio("El servicio de clima devolvió datos incompletos.") from None
