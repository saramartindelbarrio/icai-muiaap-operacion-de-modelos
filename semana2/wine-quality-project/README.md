# Wine Quality Project

Proyecto de entrenamiento de un modelo de clasificación de calidad de vino, organizado como un proyecto reproducible con `uv`.

El proyecto parte de los archivos proporcionados en `semana2/starter`:

- `WineQT.csv`
- `train.py`
- `test_train.py`

## Estructura del proyecto

```text
wine-quality-project/
├── data/
│   └── raw/
│       └── WineQT.csv
├── src/
│   └── wine_quality/
│       ├── __init__.py
│       └── train.py
├── tests/
│   └── test_train.py
├── pyproject.toml
├── uv.lock
└── README.md
```


## Instalación
uv sync --locked
Este comando instala las dependencias usando las versiones fijadas en uv.lock.

## Ejecución del entrenamiento

uv run --frozen python -m wine_quality.train
## Ejecución de los test
uv run --frozen pytest

## Comprobación con Ruff
uv run --frozen ruff check .