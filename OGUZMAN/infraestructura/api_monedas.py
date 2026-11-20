from dominio.excepciones import ErrorDeServicioExterno
from dominio.validaciones import MONEDAS_PERMITIDAS, validar_moneda
from infraestructura import config
from infraestructura.cliente_http import obtener_json


def obtener_tipo_cambio(moneda: str) -> dict:
    """Devuelve cuántos pesos chilenos vale una unidad de la moneda indicada."""
    moneda = validar_moneda(moneda)
    if not config.MONEDAS_API_URL:
        raise ErrorDeServicioExterno("El servicio de monedas no está configurado.")

    datos = obtener_json(config.MONEDAS_API_URL, "monedas")
    try:
        indicador = datos[MONEDAS_PERMITIDAS[moneda]]
        valor = float(indicador["valor"])
        fecha = str(indicador["fecha"])[:10]
    except (KeyError, TypeError, ValueError):
        raise ErrorDeServicioExterno("La respuesta del servicio de monedas está incompleta.") from None

    if valor <= 0:
        raise ErrorDeServicioExterno("El servicio de monedas entregó un valor no válido.")
    return {"moneda": moneda, "valor_clp": valor, "fecha": fecha}