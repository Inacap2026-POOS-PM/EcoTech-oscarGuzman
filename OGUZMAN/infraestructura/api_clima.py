from dominio.excepciones import ErrorDeServicioExterno
from dominio.validaciones import validar_ciudad, validar_codigo_pais
from infraestructura import config
from infraestructura.cliente_http import obtener_json


def obtener_clima(ciudad: str, codigo_pais: str | None = None) -> dict:
    """Consulta el clima actual y devuelve solo los datos que el sistema necesita."""
    consulta = validar_ciudad(ciudad)
    if codigo_pais:
        consulta = f"{consulta},{validar_codigo_pais(codigo_pais)}"

    if not config.clave_clima_configurada() or not config.CLIMA_API_URL:
        raise ErrorDeServicioExterno("El servicio de clima no está configurado.")

    datos = obtener_json(
        config.CLIMA_API_URL,
        "clima",
        params={"q": consulta, "appid": config.CLIMA_API_KEY, "units": "metric", "lang": "es"},
    )
    try:
        return {
            "ciudad": str(datos["name"]),
            "temperatura": float(datos["main"]["temp"]),
            "humedad": int(datos["main"]["humidity"]),
            "estado": str(datos["weather"][0]["description"]),
        }
    except (KeyError, IndexError, TypeError, ValueError):
        raise ErrorDeServicioExterno("La respuesta del servicio de clima está incompleta.") from None