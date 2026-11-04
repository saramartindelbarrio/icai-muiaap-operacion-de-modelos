# Problema — Construir un bundle serializado

Trabajad exclusivamente en starter/. El proyecto ya trae los contratos y el
preprocesado de la semana 3; los TODO nuevos están en artifact.py y
predict_file.py.

## Orden recomendado

1. Implementad ArtifactManifest y create_manifest() con campos estrictos.
2. Implementad save_model_bundle() y comprobad que escribe JSON y joblib.
3. Implementad load_model_bundle() validando metadatos antes del binario.
4. Implementad infer_wine_quality() y validación de la salida.
5. Implementad el CLI: validar todas las filas y escribir al final.

## Comandos

~~~bash
uv sync
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
~~~

El starter contiene un DummyClassifier en sus pruebas para evitar artefactos
grandes. Cuando el proyecto pase la suite, se puede ejecutar con un bundle real:

~~~bash
uv run python -m model_packaging.predict_file \
  --bundle models/wine_quality_bundle \
  --input ../semana3/assets/03-wine-quality/inference_samples.csv \
  --output .tmp/wine_predictions.csv
~~~

No consultéis solutions/ hasta el debrief.
