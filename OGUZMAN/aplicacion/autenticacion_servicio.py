"""Inicio de sesión con límite de intentos y bloqueo de cuenta."""
from dominio.excepciones import ErrorDeAutenticacion
from dominio.usuario import Usuario
from dominio.validaciones import validar_nombre_usuario, validar_password_login
from infraestructura.logger import obtener_logger
from infraestructura.seguridad import hashear_password, verificar_password
from infraestructura.usuario_repositorio import UsuarioRepositorio

_logger = obtener_logger()
_MENSAJE_GENERICO = "Usuario o contraseña incorrectos."
# Hash señuelo: se compara contra él cuando el usuario no existe, para que
# la respuesta tarde lo mismo y no se pueda averiguar qué usuarios existen.
_HASH_SENUELO = hashear_password("Senuelo-no-usar-1")


class AutenticacionServicio:
    """Valida credenciales, cuenta intentos fallidos y bloquea la cuenta."""

    def __init__(self):
        self._usuarios = UsuarioRepositorio()

    def iniciar_sesion(self, nombre_usuario, password) -> Usuario:
        """Devuelve el Usuario si las credenciales son correctas; si no, lanza error."""
        nombre = validar_nombre_usuario(nombre_usuario).lower()
        password = validar_password_login(password)

        usuario = self._usuarios.obtener_por_nombre(nombre)
        if usuario is None:
            verificar_password(password, _HASH_SENUELO)
            # No se registra lo escrito: alguien podría haber puesto su clave en el usuario.
            _logger.warning("Intento de ingreso con usuario inexistente")
            raise ErrorDeAutenticacion(_MENSAJE_GENERICO)

        if usuario.bloqueado:
            _logger.warning("Ingreso rechazado: cuenta bloqueada (%s)", usuario.nombre_usuario)
            raise ErrorDeAutenticacion("Cuenta bloqueada por intentos fallidos.")

        if verificar_password(password, usuario.hash_password):
            if usuario.intentos_fallidos:
                usuario.reiniciar_intentos()
                self._usuarios.actualizar_intentos(usuario)
            _logger.info("Ingreso correcto (%s)", usuario.nombre_usuario)
            return usuario

        usuario.registrar_intento_fallido()
        self._usuarios.actualizar_intentos(usuario)
        _logger.warning("Clave incorrecta (%s), intento %s",
                        usuario.nombre_usuario, usuario.intentos_fallidos)
        if usuario.bloqueado:
            raise ErrorDeAutenticacion("Demasiados intentos fallidos: la cuenta fue bloqueada.")
        raise ErrorDeAutenticacion(_MENSAJE_GENERICO)