from dominio.proyecto import Proyecto
from infraestructura.conexion import obtener_conexion

_SQL_OBTENER = "SELECT id, nombre, ciudad, pais FROM proyecto WHERE id = ?"
_SQL_LISTAR = "SELECT id, nombre, ciudad, pais FROM proyecto ORDER BY id"


class ProyectoRepositorio:
    """Guarda y recupera proyectos; traduce entre objetos del dominio y filas."""

    @staticmethod
    def _fila_a_proyecto(fila):
        """Convierte una fila de la base en un Proyecto."""
        return Proyecto(fila[0], fila[1], fila[2], fila[3])

    def guardar(self, proyecto):
        """Inserta un proyecto nuevo."""
        with obtener_conexion() as conn:
            conn.execute(
                "INSERT INTO proyecto (id, nombre, ciudad, pais) VALUES (?, ?, ?, ?)",
                (proyecto.id_proyecto, proyecto.nombre, proyecto.ciudad, proyecto.pais),
            )
        return proyecto

    def obtener(self, id_proyecto):
        """Devuelve el proyecto con ese id, o None si no existe."""
        with obtener_conexion() as conn:
            fila = conn.execute(_SQL_OBTENER, (id_proyecto,)).fetchone()
        return self._fila_a_proyecto(fila) if fila else None

    def listar(self):
        """Devuelve todos los proyectos."""
        with obtener_conexion() as conn:
            filas = conn.execute(_SQL_LISTAR).fetchall()
        return [self._fila_a_proyecto(f) for f in filas]