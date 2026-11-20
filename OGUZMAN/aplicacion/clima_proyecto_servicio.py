"""Consulta el clima del lugar de un proyecto y sugiere si conviene reprogramar."""
from dominio.excepciones import ErrorDeValidacion
from infraestructura.api_clima import obtener_clima
from infraestructura.conexion import ErrorDePersistencia
from infraestructura.consulta_repositorio import ConsultaRepositorio
from infraestructura.logger import obtener_logger
from infraestructura.proyecto_repositorio import ProyectoRepositorio

_logger = obtener_logger()
_PALABRAS_PRECIPITACION = ("lluvia", "llovizna", "tormenta", "nieve", "granizo")


def evaluar_riesgo(clima: dict) -> str:
    """Devuelve una recomendación operativa según el clima."""
    if any(p in clima["estado"].lower() for p in _PALABRAS_PRECIPITACION):
        return "Precipitaciones previstas: se recomienda reprogramar tareas al aire libre."
    if clima["temperatura"] >= 35 or clima["temperatura"] <= 0:
        return "Temperatura extrema: se recomienda ajustar horarios y medidas de seguridad."
    return "Condiciones adecuadas para trabajar."


class ClimaProyectoServicio:
    """Une proyectos, API de clima e historial local."""

    def __init__(self):
        self._proyectos = ProyectoRepositorio()
        self._consultas = ConsultaRepositorio()

    def consultar(self, id_proyecto, usuario_id) -> dict:
        """Devuelve el clima del proyecto más una recomendación."""
        proyecto = self._proyectos.obtener(id_proyecto)
        if proyecto is None:
            raise ErrorDeValidacion("No existe un proyecto con ese identificador.")
        if not proyecto.ciudad:
            raise ErrorDeValidacion("El proyecto no tiene ubicación registrada.")

        clima = obtener_clima(proyecto.ciudad, proyecto.pais)
        resultado = {"proyecto": proyecto.nombre, **clima, "recomendacion": evaluar_riesgo(clima)}
        try:
            self._consultas.guardar("clima", f"{proyecto.ciudad},{proyecto.pais}", resultado, usuario_id)
        except ErrorDePersistencia as e:
            # El historial es secundario: si falla, el usuario igual recibe su resultado.
            _logger.error("No se pudo guardar el historial de clima: %s", type(e).__name__)
        return resultado