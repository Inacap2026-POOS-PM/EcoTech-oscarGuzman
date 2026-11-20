from .validaciones import validar_ciudad, validar_codigo_pais


class Proyecto:
    """Proyecto en el que los empleados registran horas."""

    def __init__(self, id_proyecto: int, nombre: str,
                 ciudad: str | None = None, pais: str | None = None):
        """Crea el proyecto validando su nombre; la ubicación es opcional."""
        self.__id_proyecto = id_proyecto
        self.set_nombre(nombre)
        self.__ciudad = None
        self.__pais = None
        if ciudad or pais:
            self.set_ubicacion(ciudad, pais)

    @property
    def id_proyecto(self) -> int:
        """Devuelve el identificador del proyecto."""
        return self.__id_proyecto

    @property
    def nombre(self) -> str:
        """Devuelve el nombre del proyecto."""
        return self.__nombre

    @property
    def ciudad(self) -> str | None:
        """Devuelve la ciudad donde se ejecuta el proyecto, o None."""
        return self.__ciudad

    @property
    def pais(self) -> str | None:
        """Devuelve el código de país (2 letras) del proyecto, o None."""
        return self.__pais

    def set_nombre(self, valor: str) -> None:
        """Cambia el nombre; no puede estar vacío."""
        if not valor or not valor.strip():
            raise ValueError("El nombre del proyecto no puede estar vacío.")
        self.__nombre = valor.strip()

    def set_ubicacion(self, ciudad: str, pais: str) -> None:
        """Cambia la ubicación; ambos datos se validan y son obligatorios."""
        self.__ciudad = validar_ciudad(ciudad)
        self.__pais = validar_codigo_pais(pais)

    def __str__(self) -> str:
        """Devuelve la descripción del proyecto."""
        ubicacion = f" ({self.__ciudad}, {self.__pais})" if self.__ciudad else ""
        return f"Proyecto {self.__id_proyecto} - {self.__nombre}{ubicacion}"