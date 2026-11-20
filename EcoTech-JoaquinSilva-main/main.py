"""EcoTech: consulta de clima y tipo de cambio, protegida con login."""
import logging
from getpass import getpass

from almacenamiento import guardar_consulta, listar_consultas
from dominio.validaciones import (validar_ciudad, validar_moneda, validar_monto,
                                  validar_pais)
from infraestructura.api_clima import obtener_clima
from infraestructura.api_monedas import convertir_sueldo, obtener_tipo_cambio
from infraestructura.conexion import ErrorDePersistencia
from infraestructura.errores_api import ErrorServicioExterno
from infraestructura.seguridad import (MAX_INTENTOS, ErrorDeAutenticacion, autenticar,
                                       hay_usuarios, registrar_usuario)

logger = logging.getLogger("ecotech")


def configurar_registro() -> None:
    """El detalle técnico de los errores va al archivo errores.log, no a la pantalla."""
    logging.basicConfig(filename="errores.log", level=logging.WARNING,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def crear_primer_usuario() -> None:
    """Si la base no tiene usuarios, pide crear el primero (la clave no se muestra)."""
    print("No hay usuarios registrados. Crea el usuario administrador.")
    while True:
        try:
            nombre = input("Nuevo usuario: ")
            clave = getpass("Nueva contraseña: ")
            if clave != getpass("Repite la contraseña: "):
                raise ValueError("Las contraseñas no coinciden.")
            registrar_usuario(nombre, clave)
            print("Usuario creado.\n")
            return
        except ValueError as error:
            print(f"Dato inválido: {error}")


def iniciar_sesion():
    """Pide credenciales hasta MAX_INTENTOS veces; devuelve el usuario o None."""
    if not hay_usuarios():
        crear_primer_usuario()
    for intento in range(1, MAX_INTENTOS + 1):
        nombre = input("Usuario: ")
        clave = getpass("Contraseña: ")
        try:
            if autenticar(nombre, clave):
                return nombre.strip()
            print(f"Credenciales incorrectas ({intento}/{MAX_INTENTOS}).")
        except ErrorDeAutenticacion as error:
            print(f"{error} ({intento}/{MAX_INTENTOS})")
    print("Demasiados intentos fallidos. El programa se cerrará.")
    return None


def consultar_clima() -> None:
    """Pide una ciudad, consulta el clima y guarda el resultado."""
    ciudad = validar_ciudad(input("Ciudad: "))
    clima = obtener_clima(ciudad)
    print(f"{clima['ciudad']}: {clima['temperatura']} °C, "
          f"humedad {clima['humedad']} %, {clima['estado']}")
    guardar_consulta("clima", clima)


def consultar_cambio() -> None:
    """Pide una moneda, consulta su valor en pesos chilenos y guarda el resultado."""
    moneda = validar_moneda(input("Moneda (USD o EUR): "))
    cambio = obtener_tipo_cambio(moneda)
    print(f"1 {cambio['moneda']} = {cambio['valor_clp']} CLP (al {cambio['fecha']})")
    guardar_consulta("cambio", cambio)


def calcular_sueldo() -> None:
    """Convierte un sueldo en CLP a la moneda del país donde se ejecuta el proyecto."""
    pais, moneda = validar_pais(input("País del proyecto: "))
    print(f"Moneda de pago en {pais}: {moneda}")
    sueldo = validar_monto(input("Sueldo base en CLP: "))
    resultado = convertir_sueldo(sueldo, moneda)
    print(f"{resultado['sueldo_clp']:,.0f} CLP = {resultado['sueldo_convertido']:,.2f} "
          f"{moneda} (1 {moneda} = {resultado['valor_clp']} CLP, {resultado['fecha']})")
    guardar_consulta("sueldo", {**resultado, "pais": pais})


def ver_historial() -> None:
    """Muestra las últimas consultas guardadas."""
    filas = listar_consultas()
    if not filas:
        print("Aún no hay consultas guardadas.")
    for fecha, tipo, detalle in filas:
        print(f"{fecha} | {tipo} | {detalle}")


def ejecutar(accion) -> None:
    """Corre una opción del menú; cualquier fallo se informa sin detener el programa."""
    try:
        accion()
    except ValueError as error:
        print(f"Dato inválido: {error}")
    except ErrorServicioExterno as error:
        print(f"No se pudo completar la consulta: {error}")
    except ErrorDePersistencia:
        logger.exception("Falla en la base de datos")
        print("No se pudo acceder a la base de datos local. Revisa tu archivo .env.")
    except Exception:   # último recurso: el menú no debe caerse por un error imprevisto
        logger.exception("Error inesperado en el menú")
        print("Ocurrió un error inesperado. El detalle quedó en errores.log.")


OPCIONES = {"1": consultar_clima, "2": consultar_cambio,
            "3": calcular_sueldo, "4": ver_historial}


def menu(usuario: str) -> None:
    """Muestra el menú hasta que el usuario elige salir."""
    while True:
        print(f"\n== EcoTech ({usuario}) ==\n1. Clima de una ciudad\n2. Tipo de cambio\n"
              "3. Sueldo en moneda extranjera\n4. Historial\n0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            print("Hasta luego.")
            return
        accion = OPCIONES.get(opcion)
        if accion:
            ejecutar(accion)
        else:
            print("Opción no válida.")


def main() -> None:
    """Login primero: sin autenticarse no se llega al menú."""
    configurar_registro()
    try:
        usuario = iniciar_sesion()
    except ErrorDePersistencia:
        logger.exception("No se pudo iniciar la base")
        print("No se pudo acceder a la base de datos local. Revisa tu archivo .env.")
        return
    if usuario:
        menu(usuario)


if __name__ == "__main__":
    main()
