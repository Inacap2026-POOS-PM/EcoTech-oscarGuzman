"""EcoTech Solutions - ES3: login seguro + clima + pago con tipo de cambio.

Ejecutar desde la carpeta del repo:   python es3.py
"""

import getpass
import logging

from infraestructura.api_clima import obtener_clima
from infraestructura.api_monedas import convertir_pago
from infraestructura.http_cliente import ErrorDeServicio
from infraestructura.seguridad import (
    ErrorDeAutenticacion,
    autenticar,
    hay_usuarios,
    registrar_usuario,
)

MAX_INTENTOS = 3


def registrar() -> None:
    print("\n--- Registro de usuario ---")
    while True:
        usuario = input("Usuario (4-20 letras, números o _): ").strip()
        pw = getpass.getpass("Contraseña: ")
        if pw != getpass.getpass("Repite la contraseña: "):
            print("Las contraseñas no coinciden.")
            continue
        try:
            registrar_usuario(usuario, pw)
            print("Usuario registrado.\n")
            return
        except ErrorDeAutenticacion as e:
            print(e)


def iniciar_sesion() -> str | None:
    print("\n--- Inicio de sesión ---")
    for intento in range(1, MAX_INTENTOS + 1):
        usuario = input("Usuario: ").strip()
        pw = getpass.getpass("Contraseña: ")
        if autenticar(usuario, pw):
            print(f"Acceso concedido. Bienvenido/a, {usuario}.\n")
            return usuario
        print(f"Credenciales incorrectas ({intento}/{MAX_INTENTOS}).")
    print("Demasiados intentos. Acceso bloqueado.")
    return None


def opcion_clima() -> None:
    d = obtener_clima(input("Ciudad del proyecto: "))
    print(f"\nClima en {d['ciudad']}, {d['pais']}")
    print(f"  Estado:      {d['estado']}")
    print(f"  Temperatura: {d['temperatura']} °C")
    print(f"  Humedad:     {d['humedad']} %")
    print(f"  Viento:      {d['viento']} km/h")
    if d["estado"] in ("Lluvia", "Nieve", "Tormenta"):
        print("  Aviso: condición adversa, considerar reprogramar actividades al aire libre.")
    print()


def opcion_pago() -> None:
    monto = input("Monto a pagar: ")
    base = input("Moneda de origen (ej. CLP): ")
    destino = input("Moneda del país del proyecto (ej. USD): ")
    tasa, total = convertir_pago(monto, base, destino)
    print(f"\n1 {base.upper().strip()} = {tasa} {destino.upper().strip()}")
    print(f"Pago convertido: {total} {destino.upper().strip()}\n")


def menu() -> None:
    acciones = {"1": opcion_clima, "2": opcion_pago}
    while True:
        print("=== EcoTech Solutions ===")
        print("1) Consultar clima de un proyecto")
        print("2) Calcular pago con tipo de cambio")
        print("3) Salir")
        op = input("Opción: ").strip()
        if op == "3":
            print("Hasta luego.")
            return
        accion = acciones.get(op)
        if accion is None:
            print("Opción no válida.\n")
            continue
        try:
            accion()
        except ErrorDeServicio as e:
            print(f"{e}\n")  # mensaje seguro, el programa continúa
        except Exception:
            logging.exception("Error inesperado")  # detalle solo en el log
            print("Ocurrió un error inesperado. Intenta nuevamente.\n")


def main() -> None:
    try:
        if not hay_usuarios():
            print("No hay usuarios registrados. Crea el primero.")
            registrar()
        if iniciar_sesion():
            menu()
    except (KeyboardInterrupt, EOFError):
        print("\nSesión cerrada.")


if __name__ == "__main__":
    main()
