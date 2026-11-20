# EcoTech

Proyecto de clases en Python traducidas desde UML, con persistencia en SQLite.
Se corre con: `python main.py`

Líder de Proyecto: Oscar Guzmán

## Decisiones de diseño (C08)

| Decisión | La nuestra |
| --- | --- |
| ¿Se borra de verdad? | DELETE real. Al eliminar un empleado también se borra su fila en `persona`. |
| ¿Qué pasa con los hijos? | Los registros de tiempo se borran en cascada con el empleado (`ON DELETE CASCADE`). Un departamento con empleados no se puede borrar. |
| ¿Quién asigna el id? | El programa: el RUT del empleado y el código del departamento. |

# EcoTech Solutions – Unidad 3: consumo seguro de servicios externos

Extensión del sistema de gestión de EcoTech que consulta el clima de los
proyectos (OpenWeatherMap) y convierte pagos a USD o EUR con el tipo de
cambio del día (mindicador.cl), con autenticación y manejo de errores.

## Requisitos
- Python 3.10 o superior

## Instalación
```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración
1. Copiar `.env.example` como `.env`.
2. Completar `CLIMA_API_KEY` con una llave gratuita de openweathermap.org
   (se obtiene en *My API keys*; puede tardar hasta 2 horas en activarse).
   Sin llave, el sistema funciona y avisa que el clima no está configurado.

## Puesta en marcha
```
python inicializar_bd.py      # crea las tablas
python cargar_datos_demo.py   # empleados de ejemplo
python crear_usuario.py       # crea tu usuario (la clave no se muestra)
python main.py                # inicia el sistema
```

## Pruebas
```
python prueba_apis.py              # consumo de APIs y errores
python prueba_servicios.py         # clima por proyecto y pagos
python prueba_errores_seguridad.py # login, validaciones y bloqueo
```

## Seguridad implementada
- Contraseñas con hash bcrypt y salt; bloqueo tras 3 intentos fallidos.
- Mensaje único para usuario inexistente o clave incorrecta.
- Validación de entradas con listas blancas y expresiones regulares.
- Consultas SQL parametrizadas.
- API key en `.env`, fuera del código y del control de versiones.
- `timeout` y revisión de códigos HTTP en cada consulta externa.
- Errores técnicos al registro (`logs/`), mensajes genéricos al usuario.

## Estructura
- `dominio/`: clases y validaciones
- `infraestructura/`: base de datos, APIs, seguridad y registro
- `aplicacion/`: servicios que coordinan las capas
- `db/`: scripts SQL
- `docs/`: informe del uso de IA