"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.

"""Script CLI que encadena contratos, preprocesado e inferencia."""

import argparse
import csv
import os
import sys
import tempfile
from pydantic import ValidationError

from .contracts import WineQualityRequest, WineQualityPrediction
from .preprocess import preprocess_wine_request
from .inference import load_wine_quality_model, infer_wine_quality


OUTPUT_COLUMNS = [
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
]


def read_wines(path):
    """Leer el CSV y validar todas las muestras."""
    wines = []

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            sample_id = row.get("sample_id")

            if not sample_id:
                raise ValueError(f"Error en la línea {line_number}: sample_id vacío")

            # Separar sample_id de las características
            model_row = {
                key: value
                for key, value in row.items()
                if key != "sample_id"
            }

            try:
                wine = WineQualityRequest.model_validate(model_row)
                wines.append((sample_id, wine))

            except ValidationError as error:
                raise ValueError(f"Error en la línea {line_number}, muestra {sample_id}: {error}") from error
    return wines


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Predicción de calidad de vinos"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=None)

    args = parser.parse_args(argv)

    # Leer, validar y cargar el modelo
    try:
        wines = read_wines(args.input)

        if args.model is None:
            model = load_wine_quality_model()
        else:
            model = load_wine_quality_model(args.model)

        # Preprocesar y predecir todos los vinos
        predictions = []

        for sample_id, wine in wines:
            features = preprocess_wine_request(wine)
            category, confidence = infer_wine_quality(model, features)
            prediction = WineQualityPrediction(
                sample_id=sample_id,
                quality_band=category,
                confidence=confidence,
                model_version=model["model_version"],
                preprocessing_version="wine-red-features-v1",
            )

            predictions.append(prediction)

    except (ValueError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    # Crear el directorio de salida
    output_dir = os.path.dirname(os.path.abspath(args.output))
    temp_path = None


    try:
        os.makedirs(output_dir, exist_ok=True)

        # Crear un archivo temporal en el mismo directorio
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=output_dir,
            suffix=".tmp",
            delete=False
        ) as file:

            temp_path = file.name

            writer = csv.DictWriter(
                file,
                fieldnames=OUTPUT_COLUMNS
            )
            writer.writeheader()

            for prediction in predictions:
                writer.writerow(prediction.model_dump())

        # Sustituir el archivo definitivo al terminar
        os.replace(temp_path, args.output)
        temp_path = None

    except OSError as error:
        print(f"Error al guardar el archivo: {error}", file=sys.stderr)
        return 2

    finally:
        # Eliminar el temporal si algo ha fallado
        if temp_path is not None and os.path.exists(temp_path):
            os.remove(temp_path)

    print(f"Se han predicho {len(predictions)} vinos")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
