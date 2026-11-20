class ErrorServicioExterno(Exception):
    """Falla al consultar o interpretar una API externa.

    El mensaje es siempre apto para mostrarse al usuario: sin rutas, URLs ni datos internos.
    """
