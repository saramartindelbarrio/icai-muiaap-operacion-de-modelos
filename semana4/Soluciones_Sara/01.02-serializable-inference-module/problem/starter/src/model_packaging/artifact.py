"""Puntos de extensión del taller de serialización."""


from __future__ import annotations
import json 
import joblib


from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)

from model_packaging.preprocess import (
    FEATURE_NAMES,
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = (
    Path(__file__).resolve().parents[5] / "Modelo"
)
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
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
@model_validator(mode="after")
def validate_contract(self):
    if self.schema_version != ARTIFACT_SCHEMA_VERSION:
        raise ValueError("Versión del esquema incompatible")

    if self.preprocessing_version != PREPROCESSING_VERSION:
        raise ValueError("Versión del preprocesamiento incompatible")

    if self.feature_names != FEATURE_NAMES:
        raise ValueError("Características incompatibles")

    if self.output_labels != OUTPUT_LABELS:
        raise ValueError("Etiquetas incompatibles")

    if not self.model_version.strip():
        raise ValueError("La versión del modelo está vacía")

    return self


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
        feature_names=FEATURE_NAMES,
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
       
    joblib.dump(
    {"estimator": estimator},
    bundle_path / MODEL_FILENAME,
    compress=3) #Guardar el modelo entrenado

    
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
    if manifest.feature_names != FEATURE_NAMES:
        raise ValueError(
        "El orden o los nombres de las features "
        "no coinciden con el contrato esperado"
    )

    # 4.Cargar el estimador (solo si procede de una fuente confiable)
    # 4. Cargar el modelo
    payload = joblib.load(model_path)

    # Extraer el estimador del diccionario
    if not isinstance(payload, dict) or "estimator" not in payload:
        raise ValueError("El artefacto no contiene un estimador")

    estimator = payload["estimator"]

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
    features = preprocess_wine_request(request)
    matrix = [features.as_vector()]

    #Realizar la predicción
    prediccion = bundle.estimator.predict([matrix])[0]

    #Validar la etiqueta de salida
    if prediccion not in bundle.manifest.output_labels:
        raise ValueError(
            f"Etiqueta no permitida: {prediccion}"
        )

    #Obtener la confianza de la predicción
    probabilidades = bundle.estimator.predict_proba([matrix])[0]

    clases = list(bundle.estimator.classes_)
    indice = clases.index(prediccion)
    confianza = float(probabilidades[indice])

    #Construir la respuesta
    return WineQualityPrediction(
        quality_band=prediccion,
        confidence=confianza,
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )


