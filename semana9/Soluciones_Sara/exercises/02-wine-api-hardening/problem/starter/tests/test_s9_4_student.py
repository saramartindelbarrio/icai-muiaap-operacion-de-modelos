"""S9.4 — Tests que escribe el alumnado.

Cada test empieza en rojo con `pytest.fail`. Sustituye esa línea por el test
real; la entrega se considera completa cuando toda la suite está en verde.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wine_api.dependencies import get_predictor  # noqa: F401 - pista S9.4a
from wine_api.export_openapi import render_openapi
from wine_api.predictor import UnavailablePredictor  # noqa: F401 - pista S9.4a


def test_prediction_returns_503_when_model_is_unavailable(
    client: TestClient, valid_payload: dict
) -> None:
    client.app.dependency_overrides[get_predictor] = lambda: UnavailablePredictor()

    try:
        response = client.post("/v1/predictions", json=valid_payload)

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"

    finally:
        client.app.dependency_overrides.pop(get_predictor, None)


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("alcohol", 4.9),
        ("alcohol", 20.1),
        ("alcohol", None),
        ("alcohol", "mucho"),
        ("ph", 4.6),
    ],
)

# TODO S9.4b: convierte este test en @pytest.mark.parametrize con al
# menos cinco casos (justo por debajo y por encima de un rango, None, un
# texto...). Para cada uno comprueba 422 y que fields señala exactamente
# features.<campo>.
def test_out_of_contract_values_are_rejected(
    client: TestClient,
    valid_payload: dict,
    field: str,
    invalid_value: object,
) -> None:
    payload = {
        **valid_payload,
        "features": {
            **valid_payload["features"],
            field: invalid_value,
        },
    }

    response = client.post("/v1/predictions", json=payload)

    assert response.status_code == 422

    fields = response.json()["error"]["fields"]
    assert len(fields) == 1
    assert fields[0]["field"] == f"features.{field}"

    # TODO S9.4c: los límites del contrato son inclusivos. Demuéstralo con los
    # dos extremos de `alcohol` (5 y 20): ambos deben devolver 200.


@pytest.mark.parametrize("alcohol", [5.0, 20.0])
def test_range_limits_are_inclusive(
    client: TestClient,
    valid_payload: dict,
    alcohol: float,
) -> None:
    payload = {
        **valid_payload,
        "features": {
            **valid_payload["features"],
            "alcohol": alcohol,
        },
    }

    response = client.post("/v1/predictions", json=payload)

    assert response.status_code == 200


def test_openapi_matches_versioned_contract() -> None:
    # TODO S9.4d: genera `contracts/openapi.json` con
    # `uv run python -m wine_api.export_openapi` y versiónalo en Git. Después
    # compara el JSON de `render_openapi()` con el archivo: si alguien cambia el
    # contrato sin querer, este test lo detecta en la revisión.
    contract_path = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"

    saved_contract = json.loads(contract_path.read_text(encoding="utf-8"))

    current_contract = json.loads(render_openapi())

    assert current_contract == saved_contract
