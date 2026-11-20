"""Demuestra los controles de seguridad: validación, login, bloqueo y errores controlados."""
from aplicacion.autenticacion_servicio import AutenticacionServicio
from dominio.excepciones import ErrorDeDominio
from dominio.usuario import Usuario
from infraestructura.conexion import obtener_conexion
from infraestructura.seguridad import hashear_password
from infraestructura.usuario_repositorio import UsuarioRepositorio

USUARIO = "usuario_prueba"
CLAVE = "Prueba1234"

CASOS = [
    ("Usuario vacío", "", "x"),
    ("Inyección SQL en usuario", "' OR 1=1 --", "x"),
    ("Contraseña vacía", USUARIO, ""),
    ("Usuario inexistente", "no_existe", CLAVE),
    ("Clave incorrecta (1)", USUARIO, "mala"),
    ("Clave incorrecta (2)", USUARIO, "mala"),
    ("Clave correcta (reinicia intentos)", USUARIO, CLAVE),
    ("Clave incorrecta (1 de nuevo)", USUARIO, "mala"),
    ("Clave incorrecta (2 de nuevo)", USUARIO, "mala"),
    ("Clave incorrecta (3): bloqueo", USUARIO, "mala"),
    ("Clave correcta con cuenta bloqueada", USUARIO, CLAVE),
]


def borrar_usuario_prueba():
    with obtener_conexion() as conn:
        conn.execute("DELETE FROM usuarios WHERE nombre_usuario = ?", (USUARIO,))


def main():
    print("== Pruebas de seguridad ==")
    borrar_usuario_prueba()
    UsuarioRepositorio().guardar(Usuario(USUARIO, hashear_password(CLAVE)))
    servicio = AutenticacionServicio()
    try:
        for nombre, usuario, clave in CASOS:
            try:
                servicio.iniciar_sesion(usuario, clave)
                print(f"[Acceso] {nombre}")
            except ErrorDeDominio as e:
                print(f"[Rechazado] {nombre}: {e}")
    finally:
        borrar_usuario_prueba()
        print("Usuario de prueba eliminado.")


if __name__ == "__main__":
    main()