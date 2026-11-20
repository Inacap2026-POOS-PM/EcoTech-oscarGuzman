"""EcoTech Solutions - Unidad 3: consumo seguro de servicios externos."""
from getpass import getpass

from aplicacion.autenticacion_servicio import AutenticacionServicio
from aplicacion.clima_proyecto_servicio import ClimaProyectoServicio
from aplicacion.pago_internacional_servicio import PagoInternacionalServicio
from dominio.excepciones import ErrorDeDominio
from dominio.proyecto import Proyecto
from dominio.validaciones import validar_ciudad, validar_codigo_pais, validar_id_proyecto
from infraestructura.conexion import ErrorDePersistencia
from infraestructura.consulta_repositorio import ConsultaRepositorio
from infraestructura.logger import obtener_logger
from infraestructura.proyecto_repositorio import ProyectoRepositorio

MAX_INTENTOS_LOGIN = 3
_logger = obtener_logger()


def iniciar_sesion():
    """Pide credenciales hasta 3 veces; devuelve el Usuario autenticado o None."""
    servicio = AutenticacionServicio()
    for _ in range(MAX_INTENTOS_LOGIN):
        usuario = input("Usuario: ")
        password = getpass("Contraseña: ")
        try:
            return servicio.iniciar_sesion(usuario, password)
        except ErrorDeDominio as e:
            print(f"Acceso denegado: {e}")
        except ErrorDePersistencia:
            print("No se pudo verificar el acceso. Intente más tarde.")
            return None
    return None


def opcion_clima(usuario):
    id_proyecto = validar_id_proyecto(input("ID del proyecto: "))
    r = ClimaProyectoServicio().consultar(id_proyecto, usuario.id_usuario)
    print(f"\nProyecto: {r['proyecto']} ({r['ciudad']})")
    print(f"Temperatura: {r['temperatura']} °C | Humedad: {r['humedad']}% | Estado: {r['estado']}")
    print(f"Recomendación: {r['recomendacion']}")


def opcion_pago(usuario):
    rut = input("RUT del empleado (ej. 12345678-9): ")
    moneda = input("Moneda (USD o EUR): ")
    r = PagoInternacionalServicio().calcular_pago(rut, moneda, usuario.id_usuario)
    print(f"\nEmpleado: {r['empleado']}")
    print(f"Sueldo base: ${r['sueldo_clp']:,.0f} CLP")
    print(f"Tipo de cambio al {r['fecha_cambio']}: 1 {r['moneda']} = ${r['tipo_cambio_clp']:,.2f} CLP")
    print(f"Pago en {r['moneda']}: {r['monto_convertido']:,.2f}")


def opcion_registrar_proyecto(usuario):
    id_proyecto = validar_id_proyecto(input("ID del proyecto: "))
    nombre = input("Nombre del proyecto: ")
    ciudad = validar_ciudad(input("Ciudad: "))
    pais = validar_codigo_pais(input("País (código de 2 letras, ej. CL): "))
    ProyectoRepositorio().guardar(Proyecto(id_proyecto, nombre, ciudad, pais))
    print("Proyecto registrado.")


def opcion_listar_proyectos(usuario):
    proyectos = ProyectoRepositorio().listar()
    if not proyectos:
        print("No hay proyectos registrados.")
    for proyecto in proyectos:
        print(proyecto)


def opcion_historial(usuario):
    consultas = ConsultaRepositorio().listar_recientes(usuario.id_usuario)
    if not consultas:
        print("Aún no hay consultas guardadas.")
    for c in consultas:
        print(f"{c['fecha']} | {c['tipo']} | {c['parametro']}")


ACCIONES = {
    "1": ("Consultar clima de un proyecto", opcion_clima),
    "2": ("Calcular pago internacional", opcion_pago),
    "3": ("Registrar proyecto", opcion_registrar_proyecto),
    "4": ("Listar proyectos", opcion_listar_proyectos),
    "5": ("Ver mis últimas consultas", opcion_historial),
}


def menu(usuario):
    """Menú principal: solo se llega aquí después de autenticarse."""
    while True:
        print("\n--- Menú ---")
        for clave, (texto, _) in ACCIONES.items():
            print(f"{clave}. {texto}")
        print("0. Salir")
        eleccion = input("Opción: ").strip()
        if eleccion == "0":
            return
        if eleccion not in ACCIONES:
            print("Opción no válida.")
            continue
        try:
            ACCIONES[eleccion][1](usuario)
        except ErrorDeDominio as e:
            print(f"Aviso: {e}")
        except ValueError as e:
            print(f"Dato inválido: {e}")
        except ErrorDePersistencia as e:
            print(f"Error de datos: {e}")
        except Exception as e:  # último recurso: el sistema no debe caerse
            _logger.error("Error inesperado en el menú: %s", type(e).__name__)
            print("Ocurrió un error inesperado. El detalle quedó en el registro.")


def main():
    print("=== EcoTech Solutions: servicios externos ===")
    try:
        usuario = iniciar_sesion()
        if usuario is None:
            print("No fue posible autenticarse. Saliendo del sistema.")
            return
        print(f"\nBienvenido, {usuario.nombre_usuario}.")
        menu(usuario)
    except (KeyboardInterrupt, EOFError):
        print("\nSesión finalizada.")
    print("Hasta pronto.")


if __name__ == "__main__":
    main()