import os

from dotenv import load_dotenv

from infraestructura.cliente_http import get_json
from infraestructura.errores_api import ErrorServicioExterno

load_dotenv()

URL_BASE = os.environ.get("API_MONEDAS_URL", "https://mindicador.cl/api")

# Código de moneda (ISO) -> indicador de mindicador.cl, que entrega pesos chilenos.
INDICADORES = {"USD": "dolar", "EUR": "euro"}


def extraer_valor(datos: dict) -> tuple[float, str]:
    """Toma el último valor de la serie; verifica que sea un número positivo."""
    serie = datos.get("serie")
    if not isinstance(serie, list) or not serie:
        raise ErrorServicioExterno("La respuesta no trae valores del indicador.")
    try:
        valor = float(serie[0]["valor"])
        fecha = str(serie[0]["fecha"])[:10]
    except (KeyError, TypeError, ValueError) as error:
        raise ErrorServicioExterno("Valor del indicador incompleto o inválido.") from error
    if valor <= 0:
        raise ErrorServicioExterno("El valor del indicador no es utilizable.")
    return valor, fecha


def obtener_tipo_cambio(moneda: str) -> dict:
    """Devuelve {'moneda', 'valor_clp', 'fecha'}: cuántos CLP vale 1 unidad."""
    indicador = INDICADORES.get(moneda)
    if indicador is None:
        raise ErrorServicioExterno(f"Moneda no soportada: {moneda}.")
    datos = get_json(f"{URL_BASE}/{indicador}")
    valor, fecha = extraer_valor(datos)
    return {"moneda": moneda, "valor_clp": valor, "fecha": fecha}


def convertir_sueldo(sueldo_clp: float, moneda: str) -> dict:
    """Calcula el sueldo base en la moneda del país donde se ejecuta el proyecto."""
    cambio = obtener_tipo_cambio(moneda)
    return {**cambio, "sueldo_clp": sueldo_clp,
            "sueldo_convertido": round(sueldo_clp / cambio["valor_clp"], 2)}
