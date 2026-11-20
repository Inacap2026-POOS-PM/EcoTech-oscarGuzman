"""Crea un usuario del sistema pidiendo los datos por consola."""
from getpass import getpass

from dominio.excepciones import ErrorDeValidacion
from dominio.usuario import Usuario
from dominio.validaciones import validar_nombre_usuario, validar_password_nueva
from infraestructura.conexion import ErrorDeIntegridad, ErrorDePersistencia
from infraestructura.logger import obtener_logger
from infraestructura.seguridad import hashear_password
from infraestructura.usuario_repositorio import UsuarioRepositorio


def main():
    logger = obtener_logger()
    try:
        nombre = validar_nombre_usuario(input("Nuevo usuario: ").strip().lower())
        password = validar_password_nueva(getpass("Contraseña: "))
        if getpass("Repite la contraseña: ") != password:
            raise ErrorDeValidacion("Las contraseñas no coinciden.")
        UsuarioRepositorio().guardar(Usuario(nombre, hashear_password(password)))
        print("Usuario creado.")
    except ErrorDeValidacion as e:
        print(f"Dato inválido: {e}")
    except ErrorDeIntegridad:
        print("Ese nombre de usuario ya existe.")
    except ErrorDePersistencia as e:
        logger.error("Fallo de base de datos al crear usuario: %s", type(e).__name__)
        print("No se pudo crear el usuario. Revise el log.")


if __name__ == "__main__":
    main()