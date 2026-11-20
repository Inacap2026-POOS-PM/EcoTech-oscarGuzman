"""Prueba el Paso 1 con respuestas simuladas (sin internet)."""
from unittest.mock import MagicMock, patch

from infraestructura import api_clima, api_monedas
from infraestructura.errores_api import ErrorServicioExterno


def falsa(json_data):
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = json_data
    return r


GEO = {"results": [{"name": "Concepción", "latitude": -36.82, "longitude": -73.05}]}
CLIMA = {"current": {"temperature_2m": 14.2, "relative_humidity_2m": 71, "weather_code": 61}}
DOLAR = {"serie": [{"fecha": "2026-11-19T03:00:00.000Z", "valor": 948.5}]}

with patch("requests.get", side_effect=[falsa(GEO), falsa(CLIMA)]):
    print(api_clima.obtener_clima("Concepción"))
with patch("requests.get", return_value=falsa(DOLAR)):
    print(api_monedas.convertir_sueldo(950_000, "USD"))

malos = [
    (api_clima.extraer_clima, {"current": {"temperature_2m": "x"}}),
    (api_clima.extraer_clima, {"current": {"temperature_2m": 999, "relative_humidity_2m": 50, "weather_code": 0}}),
    (api_clima.extraer_clima, {}),
    (api_monedas.extraer_valor, {"serie": []}),
    (api_monedas.extraer_valor, {"serie": [{"fecha": "2026-01-01", "valor": -3}]}),
]
for funcion, datos in malos:
    try:
        funcion(datos)
        print("FALLO: aceptó datos inválidos")
    except ErrorServicioExterno as e:
        print("rechazado ->", e)
