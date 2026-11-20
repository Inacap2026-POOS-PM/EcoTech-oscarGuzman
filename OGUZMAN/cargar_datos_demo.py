"""Carga empleados de ejemplo para probar los pagos internacionales."""
from datetime import date

from dominio.empleado import Empleado
from infraestructura.conexion import ErrorDeIntegridad, ErrorDePersistencia
from infraestructura.empleado_repositorio import EmpleadoRepositorio

EMPLEADOS = [
    Empleado("12345678-9", "Ana Rojas", "Av. Costanera 123", "+56912345678",
             "ana@ecotech.cl", date(2024, 3, 1), 950_000),
    Empleado("87654321-K", "Luis Soto", "Calle 1 456", "+56987654321",
             "luis@ecotech.cl", date(2024, 6, 15), 1_200_000),
]


def main():
    repositorio = EmpleadoRepositorio()
    for empleado in EMPLEADOS:
        try:
            repositorio.guardar(empleado)
            print(f"Cargado: {empleado.nombre}")
        except ErrorDeIntegridad:
            print(f"Ya existía: {empleado.nombre}")
        except ErrorDePersistencia:
            print(f"No se pudo cargar a {empleado.nombre}. Revise el registro.")


if __name__ == "__main__":
    main()