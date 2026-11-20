import json

from infraestructura.conexion import obtener_conexion

_SQL_RECIENTES = """
    SELECT tipo, parametro, resultado, fecha
    FROM consultas_externas
    WHERE usuario_id = ?
    ORDER BY id DESC
    LIMIT ?
"""


class ConsultaRepositorio:
    """Guarda el historial de consultas a servicios externos."""

    def guardar(self, tipo, parametro, resultado, usuario_id):
        """Registra una consulta; el resultado ya viene filtrado (sin datos sensibles)."""
        with obtener_conexion() as conn:
            conn.execute(
                """INSERT INTO consultas_externas (tipo, parametro, resultado, usuario_id)
                   VALUES (?, ?, ?, ?)""",
                (tipo, parametro, json.dumps(resultado, ensure_ascii=False), usuario_id),
            )

    def listar_recientes(self, usuario_id, limite=10):
        """Devuelve las últimas consultas del usuario como lista de diccionarios."""
        with obtener_conexion() as conn:
            filas = conn.execute(_SQL_RECIENTES, (usuario_id, limite)).fetchall()
        return [
            {"tipo": f[0], "parametro": f[1], "resultado": json.loads(f[2]), "fecha": f[3]}
            for f in filas
        ]