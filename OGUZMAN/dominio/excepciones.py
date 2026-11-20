"""Excepciones propias del sistema. Permiten mostrar mensajes controlados al usuario."""


class ErrorDeDominio(Exception):
    """Base de los errores de reglas de negocio y entradas inválidas."""


class ErrorDeValidacion(ErrorDeDominio):
    """Un dato ingresado por el usuario no cumple el formato esperado."""


class ErrorDeAutenticacion(ErrorDeDominio):
    """Credenciales incorrectas, usuario bloqueado o acceso no autorizado."""


class ErrorDeServicioExterno(ErrorDeDominio):
    """Falló la consulta a una API externa (conexión, timeout, código HTTP)."""