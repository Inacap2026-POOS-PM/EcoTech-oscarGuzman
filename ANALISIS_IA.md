# Análisis crítico del uso de IA (criterio 3.1.4)

**Estudiante:** [TU NOMBRE]  ·  **Sección:** [SECCIÓN]  ·  **Herramienta de IA:** Claude (Anthropic)

## 1. Qué le pedí a la IA
[Escribe con tus palabras: p. ej. "Le pedí un script que consultara clima y tipo de cambio con
requests, con login seguro, manejo de errores y guardado local".]

## 2. Vulnerabilidades y riesgos que revisé en el código generado
| # | Riesgo (típico en código generado por IA) | Dónde lo revisé | Decisión |
|---|---|---|---|
| 1 | Guardar contraseñas en texto plano o con hash simple (MD5/SHA sin salt) | `infraestructura/seguridad.py` (`registrar_usuario`) | **Modificado/validado:** PBKDF2-HMAC-SHA256, salt aleatorio de 16 bytes, 310.000 iteraciones |
| 2 | Comparar hashes con `==` (ataque por tiempo) | `seguridad.autenticar` | Se usa `hmac.compare_digest` |
| 3 | SQL armado con f-strings (inyección SQL) | todas las consultas a SQLite | Solo consultas **parametrizadas** (`?`) |
| 4 | Entradas sin validar (ciudad, moneda, monto) | `api_clima.py`, `api_monedas.py`, `seguridad.py` | Regex de lista blanca, `Decimal`, rechazo de NaN/negativos/valores enormes |
| 5 | `requests.get` sin `timeout` (el programa se cuelga) | `http_cliente.pedir_json` | `timeout=10` y 2 reintentos |
| 6 | `except:` genérico que oculta errores o muestra trazas con datos internos | `http_cliente.py`, `es3.py` | Excepción propia `ErrorServicio` con mensaje seguro; el detalle va solo a `ecotech.log` |
| 7 | API keys escritas en el código | `http_cliente.py` | Se lee con `os.getenv` de la variable de entorno `ECOTECH_API_KEY`; `.env` en `.gitignore` |
| 8 | No revisar el código HTTP de la respuesta | `http_cliente.pedir_json` | Se manejan 200, 404, 401/403, 429, 5xx y otros |
| 9 | Mensajes de login que revelan si el usuario existe | `seguridad.autenticar` | Mensaje genérico + hash calculado siempre |
| 10 | Sin límite de intentos de login | `seguridad.autenticar` | Bloqueo tras 3 intentos |

## 3. Qué ajusté, qué descarté y por qué
- [Completa con TUS palabras al menos 2–3 decisiones. Ejemplo: "Descarté guardar usuarios en un
  JSON y usé SQLite porque permite consultas parametrizadas y es más ordenado".]
- [Ejemplo: "Mantuve Open-Meteo porque no requiere llave, lo que reduce el riesgo de filtrarla".]

## 4. Cómo verifiqué la seguridad
- Ejecuté **Bandit** (`bandit -r .`): [pega aquí tu resultado/captura].
- Probé entradas inválidas: ciudad `x; DROP TABLE`, monto `-5`, moneda `U1`, contraseña vacía.
- Simulé errores 404, 500 y caída de conexión: el programa continúa y no muestra información sensible.

## 5. Limitaciones y mejoras futuras
- [Ej.: usar bcrypt/argon2, agregar roles de usuario, caché de consultas, pruebas unitarias.]
