"""Prueba el consumo de APIs y el manejo de errores sin que el programa se caiga."""
from dominio.excepciones import ErrorDeDominio
from infraestructura.api_clima import obtener_clima
from infraestructura.api_monedas import obtener_tipo_cambio

CASOS = [
    ("Dólar", lambda: obtener_tipo_cambio("usd")),
    ("Euro", lambda: obtener_tipo_cambio("EUR")),
    ("Moneda no permitida", lambda: obtener_tipo_cambio("xyz")),
    ("Clima Concepción", lambda: obtener_clima("Concepción", "CL")),
    ("Ciudad inválida", lambda: obtener_clima("Santiago; DROP")),
    ("Ciudad inexistente", lambda: obtener_clima("Zzzzqqxx")),
]

for nombre, caso in CASOS:
    try:
        print(f"[OK] {nombre}: {caso()}")
    except ErrorDeDominio as e:
        print(f"[Controlado] {nombre}: {e}")