class Usuario:
    """Usuario del sistema. Solo guarda el hash de la contraseña, nunca la clave."""

    MAX_INTENTOS = 3

    def __init__(self, nombre_usuario: str, hash_password: str,
                 id_usuario: int | None = None, intentos_fallidos: int = 0,
                 bloqueado: bool = False):
        """Crea el usuario; id, intentos y bloqueo vienen de la base al recuperarlo."""
        self.__id_usuario = id_usuario
        self.__nombre_usuario = nombre_usuario
        self.__hash_password = hash_password
        self.__intentos_fallidos = intentos_fallidos
        self.__bloqueado = bloqueado

    @property
    def id_usuario(self) -> int | None:
        """Devuelve el identificador del usuario, o None si aún no se guarda."""
        return self.__id_usuario

    @property
    def nombre_usuario(self) -> str:
        """Devuelve el nombre de usuario."""
        return self.__nombre_usuario

    @property
    def hash_password(self) -> str:
        """Devuelve el hash de la contraseña (nunca la clave original)."""
        return self.__hash_password

    @property
    def intentos_fallidos(self) -> int:
        """Devuelve la cantidad de intentos fallidos consecutivos."""
        return self.__intentos_fallidos

    @property
    def bloqueado(self) -> bool:
        """Indica si la cuenta está bloqueada."""
        return self.__bloqueado

    def registrar_intento_fallido(self) -> None:
        """Suma un intento fallido y bloquea la cuenta al llegar al máximo."""
        self.__intentos_fallidos += 1
        if self.__intentos_fallidos >= self.MAX_INTENTOS:
            self.__bloqueado = True

    def reiniciar_intentos(self) -> None:
        """Vuelve el contador a cero tras un ingreso correcto."""
        self.__intentos_fallidos = 0

    def __str__(self) -> str:
        """Describe al usuario sin mostrar su hash."""
        estado = "bloqueado" if self.__bloqueado else "activo"
        return f"Usuario {self.__nombre_usuario} ({estado})"