from dominio.usuario import Usuario
from infraestructura.conexion import obtener_conexion

# Los datos del usuario viajan siempre aparte, como parámetros (?).
_SQL_OBTENER = """
    SELECT id, nombre_usuario, hash_password, intentos_fallidos, bloqueado
    FROM usuarios
    WHERE nombre_usuario = ?
"""


class UsuarioRepositorio:
    """Guarda y recupera usuarios; traduce entre objetos del dominio y filas."""

    @staticmethod
    def _fila_a_usuario(fila):
        """Convierte una fila de la base en un Usuario."""
        return Usuario(
            id_usuario=fila[0],
            nombre_usuario=fila[1],
            hash_password=fila[2],
            intentos_fallidos=fila[3],
            bloqueado=bool(fila[4]),
        )

    def guardar(self, usuario):
        """Inserta un usuario nuevo y devuelve su id."""
        with obtener_conexion() as conn:
            cur = conn.execute(
                "INSERT INTO usuarios (nombre_usuario, hash_password) VALUES (?, ?)",
                (usuario.nombre_usuario, usuario.hash_password),
            )
        return cur.lastrowid

    def obtener_por_nombre(self, nombre_usuario):
        """Devuelve el usuario con ese nombre, o None si no existe."""
        with obtener_conexion() as conn:
            fila = conn.execute(_SQL_OBTENER, (nombre_usuario,)).fetchone()
        return self._fila_a_usuario(fila) if fila else None

    def actualizar_intentos(self, usuario):
        """Guarda intentos fallidos y bloqueo; devuelve cuántas filas cambiaron."""
        with obtener_conexion() as conn:
            cur = conn.execute(
                "UPDATE usuarios SET intentos_fallidos = ?, bloqueado = ? WHERE id = ?",
                (usuario.intentos_fallidos, int(usuario.bloqueado), usuario.id_usuario),
            )
        return cur.rowcount