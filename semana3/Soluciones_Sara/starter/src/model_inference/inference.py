"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

"""Carga del modelo e inferencia."""

from pathlib import Path
import joblib
import pandas as pd

from .preprocess import FEATURE_NAMES, WineFeatures


DEFAULT_MODEL_PATH = (Path(__file__).resolve().parent / "wine_quality_model.joblib")


def load_wine_quality_model(model_path=DEFAULT_MODEL_PATH):
    # Cargar el modelo
    model = joblib.load(model_path)

    # Comprobar que contiene un clasificador
    if not isinstance(model, dict):
        raise ValueError("Artefacto inválido")

    if "estimator" not in model or not callable(getattr(model["estimator"], "predict", None)):
        raise ValueError("El modelo no contiene un clasificador compatible")

    # Comprobar el orden de las características
    if tuple(model.get("feature_names", ())) != FEATURE_NAMES:
        raise ValueError("feature_names incorrecto")

    return model


def infer_wine_quality(model, features: WineFeatures):
    # Comprobar el orden
    if tuple(model["feature_names"]) != FEATURE_NAMES:
        raise ValueError("feature_names incorrecto")

    # Preparar el vector
    X = pd.DataFrame(
        [features.as_vector()],
        columns=FEATURE_NAMES
    )

    # Predecir la calidad del vino
    prediction = model["estimator"].predict(X)[0]

    # Calcular la confianza
    probabilities = model["estimator"].predict_proba(X)[0]
    confidence = float(max(probabilities))

    return str(prediction), confidence
