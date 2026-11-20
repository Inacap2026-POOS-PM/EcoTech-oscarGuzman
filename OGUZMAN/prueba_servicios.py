"""Prueba los servicios de clima y pago internacional con casos buenos y malos."""
from aplicacion.clima_proyecto_servicio import ClimaProyectoServicio
from aplicacion.pago_internacional_servicio import PagoInternacionalServicio
from dominio.excepciones import ErrorDeDominio
from dominio.proyecto import Proyecto
from infraestructura.conexion import ErrorDeIntegridad, ErrorDePersistencia
from infraestructura.proyecto_repositorio import ProyectoRepositorio
from infraestructura.usuario_repositorio import UsuarioRepositorio

usuario = UsuarioRepositorio().obtener_por_nombre(input("Usuario existente: ").strip().lower())
if usuario is None:
    raise SystemExit("Ese usuario no existe. Créalo con crear_usuario.py.")

try:
    ProyectoRepositorio().guardar(Proyecto(1, "Parque solar Biobío", "Concepción", "CL"))
    print("Proyecto de prueba creado.")
except ErrorDeIntegridad:
    print("El proyecto de prueba ya existía.")

clima, pagos = ClimaProyectoServicio(), PagoInternacionalServicio()
CASOS = [
    ("Clima proyecto 1", lambda: clima.consultar(1, usuario.id_usuario)),
    ("Proyecto inexistente", lambda: clima.consultar(999, usuario.id_usuario)),
    ("Pago USD", lambda: pagos.calcular_pago("12345678-9", "usd", usuario.id_usuario)),
    ("Pago EUR", lambda: pagos.calcular_pago("12345678-9", "EUR", usuario.id_usuario)),
    ("RUT mal escrito", lambda: pagos.calcular_pago("123", "USD", usuario.id_usuario)),
    ("Empleado inexistente", lambda: pagos.calcular_pago("11111111-1", "USD", usuario.id_usuario)),
    ("Moneda no permitida", lambda: pagos.calcular_pago("12345678-9", "BTC", usuario.id_usuario)),
]
for nombre, caso in CASOS:
    try:
        print(f"[OK] {nombre}: {caso()}")
    except ErrorDeDominio as e:
        print(f"[Controlado] {nombre}: {e}")
    except ErrorDePersistencia:
        print(f"[Controlado] {nombre}: error de base de datos.")