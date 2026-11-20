"""Calcula el pago de un empleado convertido a una moneda extranjera."""
from dominio.excepciones import ErrorDeValidacion
from dominio.validaciones import validar_moneda, validar_rut
from infraestructura.api_monedas import obtener_tipo_cambio
from infraestructura.conexion import ErrorDePersistencia
from infraestructura.consulta_repositorio import ConsultaRepositorio
from infraestructura.empleado_repositorio import EmpleadoRepositorio
from infraestructura.logger import obtener_logger

_logger = obtener_logger()


class PagoInternacionalServicio:
    """Une empleados, API de monedas e historial local."""

    def __init__(self):
        self._empleados = EmpleadoRepositorio()
        self._consultas = ConsultaRepositorio()

    def calcular_pago(self, rut, moneda, usuario_id) -> dict:
        """Convierte el sueldo base (CLP) a la moneda elegida usando el tipo de cambio actual."""
        rut = validar_rut(rut)
        moneda = validar_moneda(moneda)
        empleado = self._empleados.obtener(rut)
        if empleado is None:
            raise ErrorDeValidacion("No existe un empleado con ese RUT.")

        cambio = obtener_tipo_cambio(moneda)
        resultado = {
            "empleado": empleado.nombre,
            "sueldo_clp": empleado.salario,
            "moneda": moneda,
            "tipo_cambio_clp": cambio["valor_clp"],
            "fecha_cambio": cambio["fecha"],
            "monto_convertido": round(empleado.salario / cambio["valor_clp"], 2),
        }
        try:
            self._consultas.guardar("moneda", f"{rut} -> {moneda}", resultado, usuario_id)
        except ErrorDePersistencia as e:
            _logger.error("No se pudo guardar el historial de pago: %s", type(e).__name__)
        return resultado