from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Body

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.schemas import (
    VALID_FEATURES_EXAMPLE,
    ErrorResponse,
    Prediction,
    PredictionRequest,
    PredictionResponse,
)

# TODO S9.3a: mueve aquí `prefix="/v1/predictions"` y `tags=["predictions"]`.
# TODO S9.3c: declara a nivel de router `responses=` para 400, 422 y 503 con
# `{"model": ErrorResponse, "description": ...}`. Así el 422 deja de
# documentarse como `HTTPValidationError`, que ya no es lo que devolvemos.

router = APIRouter(
    prefix="/v1/predictions",
    tags=["predictions"],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid JSON",
        },
        422: {
            "model": ErrorResponse,
            "description": "Invalid input",
        },
        503: {
            "model": ErrorResponse,
            "description": "Prediction model unavailable",
        },
    },
)
# TODO S9.3e: añade summary, response_description y un docstring útil para
# quien consume la API (campos, rangos, decimales de confidence).
# TODO S9.3f: ofrece en Swagger al menos tres ejemplos de cuerpo (uno válido
# y dos inválidos). Investiga `Annotated[PredictionRequest, Body(...)]` con
# `openapi_examples=`; usa VALID_FEATURES_EXAMPLE como base.


@router.post(
    "",
    response_model=PredictionResponse,  # noqa: FAST001
    summary="Predecir la calidad de un vino",
    response_description="Predicción con confianza, versiones y trazabilidad.",
)
def create_prediction(
    payload: Annotated[
        PredictionRequest,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Vino válido",
                    "value": {
                        "features": VALID_FEATURES_EXAMPLE,
                    },
                },
                "invalid_alcohol": {
                    "summary": "Alcohol fuera de rango",
                    "value": {
                        "features": {
                            **VALID_FEATURES_EXAMPLE,
                            "alcohol": 25.0,
                        },
                    },
                },
                "missing_alcohol": {
                    "summary": "Falta el campo alcohol",
                    "value": {
                        "features": {
                            key: value
                            for key, value in VALID_FEATURES_EXAMPLE.items()
                            if key != "alcohol"
                        },
                    },
                },
            },
        ),
    ],
    predictor: PredictorDep,
    request_id: RequestIdDep,
) -> PredictionResponse:
    """Predice la calidad de un vino tinto a partir de sus características.

    Recibe 11 variables fisicoquímicas dentro del objeto `features`,
    incluyendo acidez, densidad, pH, sulfatos y alcohol.

    Cada variable debe respetar los rangos definidos en `WineFeatures`.
    Por ejemplo, `alcohol` debe estar entre 5 y 20 (% vol.)
    y `ph` entre 2.5 y 4.5.

    La respuesta incluye la categoría de calidad (`quality_band`),
    la confianza (`confidence`) redondeada a dos decimales,
    las versiones del modelo y del preprocesamiento,
    un `request_id` y la fecha de respuesta (`served_at`).

    El campo interno `raw_score` no se expone al cliente.
    """

    output = predictor.predict(
        payload.features
    )  # llama al predictor para calcular la calidad del vino
    # TODO S9.1e: este dict expone `raw_score` y la confianza sin redondear.
    # Declara `-> PredictionResponse` y construye el modelo; para pasar de la
    # dataclass ModelOutput a Prediction investiga `from_attributes=True`.
    prediction = Prediction.model_validate(
        output,
        from_attributes=True,
    )
    return PredictionResponse(
        prediction=prediction,
        request_id=request_id,
        served_at=datetime.now(UTC),
    )
