from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# TODO: clase PrestamoEntrada (BaseModel) con las 6 variables del modelo, con sus rangos (ver enunciado).
#       Debe rechazar campos que no existan.
# TODO: field_validator (con classmethod) para antiguedad_laboral_anios: no puede ser incoherente con la edad.
# TODO: clase PrediccionSalida con probabilidad_impago (entre 0 y 1) y decision (aprobar, revisar o rechazar).

class PrestamoEntrada(BaseModel):
    model_config = ConfigDict(extra = "forbid")
    edad : int = Field(ge=18, le=75)
    ingresos_mensuales : float = Field(gt = 0)
    importe_prestamo : float = Field(gt = 0)
    plazo_meses : int = Field(ge = 6, le= 84 )
    antiguedad_laboral_anios : int = Field(ge=0, le = 50)
    impagos_previos: int = Field(ge=0, le=20)
    @field_validator("antiguedad_laboral_anios", mode="before")
    @classmethod
    def edad_not_incoherent(cls, value, info):
        edad = info.data.get("edad")
        if edad is not None and value > edad - 16:
                raise ValueError("La antigüedad laboral no puede superar la edad menos 16")
        return value

class PrediccionSalida(BaseModel):
    probabilidad_impago : float = Field(ge= 0, le = 1)
    decision : Literal["aprobar", "revisar", "rechazar"]




