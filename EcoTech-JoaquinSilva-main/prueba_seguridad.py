"""Prueba el Paso 2 en una base temporal: hash, login y validaciones."""
import os
import tempfile

os.environ["DB_NOMBRE"] = os.path.join(tempfile.mkdtemp(), "prueba.db")

from dominio import validaciones as v
from infraestructura import seguridad as s

# --- Hash ---
h1, h2 = s.hashear_password("Clave1234"), s.hashear_password("Clave1234")
print("hash distinto con misma clave (sal):", h1 != h2)
print("'Clave1234' en el hash?:", "Clave1234" in h1)

# --- Login ---
print("hay usuarios al inicio:", s.hay_usuarios())
s.registrar_usuario("admin", "Clave1234")
print("login correcto:", s.autenticar("admin", "Clave1234"))
print("clave incorrecta:", s.autenticar("admin", "otraClave1"))
print("usuario inexistente:", s.autenticar("fantasma", "Clave1234"))
for u, p in [("", "x"), ("admin", "")]:
    try:
        s.autenticar(u, p)
        print("FALLO: aceptó vacío")
    except s.ErrorDeAutenticacion as e:
        print("vacío rechazado ->", e)

with s.obtener_conexion() as c:
    print("guardado en BD:", c.execute("SELECT clave_hash FROM usuario").fetchone()[0][:30], "...")

# --- Validaciones ---
casos = [
    (v.validar_ciudad, "Concepción"), (v.validar_ciudad, "'; DROP TABLE x;--"),
    (v.validar_ciudad, ""), (v.validar_ciudad, "123"),
    (v.validar_moneda, "usd"), (v.validar_moneda, "XYZ"),
    (v.validar_password, "corta"), (v.validar_password, "sinmayuscula1"),
    (v.validar_usuario, "ab"), (v.validar_usuario, "joaquin_jk"),
]
for f, x in casos:
    try:
        print(f"{f.__name__}({x!r}) -> OK:", f(x))
    except ValueError as e:
        print(f"{f.__name__}({x!r}) -> rechazado:", e)
