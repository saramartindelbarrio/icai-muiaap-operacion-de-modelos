from fastapi import APIRouter

from wine_api.dependencies import PredictorDep, RequestIdDep
from wine_api.errors import ModelUnavailableError
from wine_api.schemas import ErrorResponse, HealthResponse  # noqa: F401 - pista para S9.1d

SERVICE_NAME = "wine-quality-prediction"

# TODO S9.3a: declara `tags=["health"]` en el router, no en include_router().
router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        503: {
            "model": ErrorResponse,
            "description": "Prediction model unavailable",
        },
    },
)


# TODO S9.3b: añade `summary=`, `response_description=` y un docstring que diga
# cuándo usar el endpoint y qué significa un 503. Documenta el 503 con
# `responses={503: {"model": ErrorResponse, "description": ...}}`.
@router.get(
    "",
    response_model=HealthResponse,  # noqa: FAST001
    summary="Consultar el estado del servicio",
    response_description="Estado de la API y disponibilidad del modelo de predicción.",
)
def read_health(predictor: PredictorDep, request_id: RequestIdDep) -> HealthResponse:
    """Comprueba el estado de la API y la disponibilidad del modelo.
    Devuelve información del servicio, la versión del modelo y el
    identificador de la petición. Si el modelo no está disponible,
    la API devuelve un error HTTP 503.
    """
    # TODO S9.2f: sustituye el HTTPException por `ModelUnavailableError`: el
    # dominio no debería saber de HTTP y el manejador produce el sobre común.
    if not predictor.is_ready():
        raise ModelUnavailableError()
    # TODO S9.1d: declara `-> HealthResponse` y devuelve una instancia.
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        model_status="ready",
        model_version=predictor.model_version,
        request_id=request_id,
    )
