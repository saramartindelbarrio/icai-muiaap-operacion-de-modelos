"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import csv

import argparse
from pathlib import Path

from model_packaging.artifact import DEFAULT_BUNDLE_PATH
from model_packaging.contracts import WineQualityRequest
from model_packaging.artifact import (
    load_model_bundle,
    infer_wine_quality,
)

def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    # 1. Cargar el modelo y su manifiesto
    bundle = load_model_bundle(bundle_path)

    # 2. Leer el CSV de entrada
    with input_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("El CSV no tiene cabecera")

        # Comprobar las columnas esperadas
        expected = [
            "sample_id",
            *bundle.manifest.feature_names
        ]

        if reader.fieldnames != expected:
            raise ValueError(
                "Las columnas del CSV no coinciden "
                "con el contrato de entrada"
            )

        rows = list(reader)

    # 3. Validar todas las filas y predecir
    predictions = []

    for numero, row in enumerate(rows, start=2):

        try:
        # Separar el identificador de la muestra
            sample_id = row["sample_id"]

            # Extraer únicamente las 11 features
            features = {
                name: row[name]
                for name in bundle.manifest.feature_names
            }

            # Validar las features  
            request = WineQualityRequest.model_validate(features)  
            prediction = infer_wine_quality(bundle, request)       
            result = {
                "sample_id": sample_id,
                **prediction.model_dump(mode="json")
            }

            predictions.append(result) 

        except Exception as exc:
            raise ValueError(
                f"Error en la fila {numero}: {exc}"
            ) from exc

    # 4. Escribir el CSV al terminar todas las predicciones
    output_columns = [
        "sample_id",
        "quality_band",
        "confidence",
        "model_version",
        "preprocessing_version",
    ]

    with output_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=output_columns
        )

        writer.writeheader()
        writer.writerows(predictions)

    # 5. Devolver cuántas filas se procesaron
    return len(predictions)

def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
