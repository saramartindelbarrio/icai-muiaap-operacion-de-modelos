# S10.7 — Informe de carga

> **TODO S10.7c:** ejecuta Locust con `--csv reports/s10`, versiona los CSV
> generados y completa las tablas y el análisis de este archivo.

Plantilla del informe. Rellénala con **tus** resultados: dependen de la máquina,
del número de workers y de la configuración de `.env`. No copies cifras de otra
persona ni de la solución, que no incluye resultados.

## Cómo se ha medido
| Dato | Valor |
| :--- | :--- |
| Comando de la API | `uv run --locked fastapi dev --host 127.0.0.1 --port 8001` (1 proceso) |
| Comando de Locust | `uv run --group load --locked python -m locust -f locustfile.py --headless -u 20 -r 5 -t 1m --host http://127.0.0.1:8001 --csv reports/s10` |
| Cliente usado | `front` |
| `rate_limit_per_minute` del cliente | 60 |
| Máquina | Intel Core i7-1165G7 @ 2.80 GHz; Windows con Ubuntu WSL2 |
| Usuarios simulados | 20 |
| Tasa de incorporación | 5 usuarios/s |
| Duración | 1 minuto |
| Versión de Locust | 2.46.7 |

Se utilizó WSL2 porque la política de seguridad de Windows impedía cargar las bibliotecas nativas de gevent necesarias para Locust.

Los archivos generados y conservados junto a este informe son s10_stats.csv, s10_failures.csv y s10_stats_history.csv.

## Resultados

Copia los valores de la fila `POST /v1/predictions` y de `Aggregated` de
`s10_stats.csv`.

| Endpoint | Peticiones | RPS | p50 (ms) | p95 (ms) | Fallos | % 429 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `POST /v1/predictions` | 746 | 12,64 | 7 | 13 | 690 | 92,49 % |
| `/v1/predictions [422]` | 96 | 1,63 | 7 | 11 | 92 | — |
| `GET /health` | 86 | 1,46 | 5 | 8 | 0 | — |
| Aggregated | 928 | 15,73 | 7 | 13 | 782 | 84,27 % |

El porcentaje de respuestas HTTP `429` de las predicciones válidas se ha calculado como:

**690 / 746 × 100 = 92,49 %.**

El porcentaje agregado de fallos se calcula como:

**782 / 928 × 100 = 84,27 %.**

Los 782 fallos registrados corresponden a respuestas HTTP `429`: 690 en predicciones válidas y 92 en predicciones con datos inválidos que esperaban recibir un `422`.



## Análisis (5–10 líneas)

- ¿Cuántas predicciones por minuto deja pasar el límite y cuántas ha pedido
  Locust? ¿Cuadra el `% 429` con esa cuenta?
- ¿Qué latencia (p50, p95) tiene `GET /health`, que no pasa por autenticación ni
  rate limit, frente a `POST /v1/predictions`?
- ¿Qué cambiaría con dos workers (`fastapi run --workers 2`) y un contador en
  memoria por proceso?
- Si quisieras medir la capacidad del servicio y no la política de cuotas, ¿qué
  cliente y qué límite usarías?

El cliente front tenía un límite de 60 peticiones por minuto, mientras que Locust realizó 852 solicitudes de predicción, contando válidas e inválidas.
De ellas, 60 fueron admitidas por el control de cuota: 56 predicciones válidas y 4 peticiones inválidas que recibieron correctamente HTTP 422.
Las otras 792 fueron rechazadas con HTTP 429, lo que demuestra que el límite de peticiones se aplicó durante la prueba.
En las predicciones válidas, el porcentaje de rechazos fue del 92,57 %, coherente con la diferencia entre la demanda simulada y la cuota disponible.

GET /health tuvo una latencia p50 de 5 ms y p95 de 8 ms, frente a 7 ms y 13 ms de POST /v1/predictions.
/health no requiere autenticación ni rate limiting y completó sus 88 peticiones sin fallos.
Los tiempos de predicción deben interpretarse con cautela, porque muchas solicitudes recibieron rápidamente un 429 sin ejecutar el modelo.

Con dos workers y un contador en memoria por proceso, cada worker mantendría su propio contador; por tanto, el límite efectivo podría superar las 60 peticiones por minuto si el tráfico se repartiera entre ambos.
Para aplicar una cuota global entre varios workers sería necesario utilizar un almacenamiento compartido para los contadores, por ejemplo Redis.

Para medir la capacidad real del servicio, utilizaría un cliente de pruebas con permiso predict y una cuota suficientemente elevada para que el rate limiting no condicionase los resultados.

