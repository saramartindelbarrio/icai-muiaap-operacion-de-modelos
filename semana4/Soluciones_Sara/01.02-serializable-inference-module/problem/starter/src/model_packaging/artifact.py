"""Puntos de extensión del taller de serialización."""


from __future__ import annotations
import json 
import joblib


from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)
EXPECTED_FEATURE_NAMES= (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
    )

class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1)


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:  


    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version="wine-red-features-v1",
        feature_names=EXPECTED_FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )

   

def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """TODO: escribe manifest.json y model.joblib de forma segura."""
    bundle_path.mkdir(parents=True, exist_ok=True) #Creamos el directorio si no existe
    if manifest is None: #Se crea el manifiesto si no se proporciona
        manifest = create_manifest(
            estimator,
            model_version="wine-quality-rf-demo-v1"
        )
       
    joblib.dump(estimator, bundle_path / MODEL_FILENAME) #Guardar el modelo entrenado

    
    with (bundle_path / MANIFEST_FILENAME).open( #Guardar el manifiesto
        "w", encoding="utf-8"
    ) as file:
        json.dump(
            manifest.model_dump(mode="json"),
            file,
            indent=2,
            ensure_ascii=False
        )

    return manifest     

 


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """TODO: valida el manifiesto antes de cargar el estimador."""
    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME

    # 1.Comprobar que existen los archivos
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"No se encuentra el manifiesto: {manifest_path}"
        )

    if not model_path.is_file():
        raise FileNotFoundError(
            f"No se encuentra el modelo: {model_path}"
        )

    # 2.Leer y validar la estructura del manifiesto
    with manifest_path.open("r", encoding="utf-8") as file:
        manifest_data = json.load(file)

    manifest = ArtifactManifest.model_validate(manifest_data)

    # 3.Comprobar la versión del esquema
    if manifest.schema_version != ARTIFACT_SCHEMA_VERSION:
        raise ValueError(
            "La versión del esquema no es compatible"
        )
    if manifest.feature_names != EXPECTED_FEATURE_NAMES:
        raise ValueError(
        "El orden o los nombres de las features "
        "no coinciden con el contrato esperado"
    )

    # 4.Cargar el estimador (solo si procede de una fuente confiable)
    estimator = joblib.load(model_path)

    # 5.Comprobar el tipo de estimador
    if type(estimator).__name__ != manifest.estimator_type:
        raise ValueError(
            "El tipo de estimador no coincide con el manifiesto"
        )

    # 6. Devolver el bundle
    return LoadedModelBundle(
        estimator=estimator,
        manifest=manifest
    )




def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""
    # 1. Obtener los datos de entrada
    datos = request.model_dump()

    # 2. Colocar las features en el orden correcto
    features = [
        float(datos[name])
        for name in bundle.manifest.feature_names
    ]

    # 3. Realizar la predicción
    prediccion = bundle.estimator.predict([features])[0]

    # 4. Validar la etiqueta de salida
    if prediccion not in bundle.manifest.output_labels:
        raise ValueError(
            f"Etiqueta no permitida: {prediccion}"
        )

    # 5. Obtener la confianza de la predicción
    probabilidades = bundle.estimator.predict_proba([features])[0]

    clases = list(bundle.estimator.classes_)
    indice = clases.index(prediccion)
    confianza = float(probabilidades[indice])

    # 6. Construir la respuesta
    return WineQualityPrediction(
        quality_band=prediccion,
        confidence=confianza,
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )