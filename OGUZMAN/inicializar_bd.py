"""Crea las tablas aplicando en orden los archivos .sql de la carpeta db/."""
from pathlib import Path

from infraestructura.conexion import ErrorDePersistencia, obtener_conexion

RUTA_DB = Path(__file__).resolve().parent / "db"


def main():
    scripts = sorted(RUTA_DB.glob("*.sql"))
    try:
        with obtener_conexion() as conn:
            for script in scripts:
                conn.executescript(script.read_text(encoding="utf-8"))
                print(f"Aplicado: {script.name}")
    except (ErrorDePersistencia, OSError):
        print("No se pudo inicializar la base de datos. Revise la configuración.")
        return
    print("Base de datos lista.")


if __name__ == "__main__":
    main()