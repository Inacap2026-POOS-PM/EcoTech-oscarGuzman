"""Prueba el Paso 3: el programa no se cae y los mensajes no filtran datos."""
from unittest.mock import MagicMock, patch

import requests

from infraestructura import cliente_http
from infraestructura.errores_api import ErrorServicioExterno


def resp(codigo, json_data=None, json_malo=False):
    r = MagicMock()
    r.status_code = codigo
    if json_malo:
        r.json.side_effect = ValueError("no es json")
    else:
        r.json.return_value = json_data or {}
    return r


casos = {
    "Timeout (3 intentos)": dict(side_effect=requests.exceptions.Timeout("C:\\Users\\secreto")),
    "Sin conexión": dict(side_effect=requests.exceptions.ConnectionError("host interno")),
    "Error genérico": dict(side_effect=requests.exceptions.RequestException("x")),
    "HTTP 404": dict(return_value=resp(404)),
    "HTTP 429": dict(return_value=resp(429)),
    "HTTP 500": dict(return_value=resp(500)),
    "HTTP 403": dict(return_value=resp(403)),
    "200 sin JSON": dict(return_value=resp(200, json_malo=True)),
}
with patch("time.sleep"):
    for nombre, config in casos.items():
        with patch("requests.get", **config) as falso:
            try:
                cliente_http.get_json("https://ejemplo.cl/api")
                print(nombre, "-> FALLO: no lanzó error")
            except ErrorServicioExterno as e:
                filtra = any(p in str(e) for p in ("C:\\", "secreto", "http", "host"))
                print(f"{nombre}: llamadas={falso.call_count} -> '{e}' | filtra datos: {filtra}")

# Se recupera si el segundo intento funciona
with patch("time.sleep"), patch("requests.get",
          side_effect=[requests.exceptions.Timeout(), resp(200, {"ok": 1})]) as falso:
    print("Reintento exitoso:", cliente_http.get_json("https://ejemplo.cl"), "llamadas:", falso.call_count)
