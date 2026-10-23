
from pydantic import BaseModel, Field, field_validator



class WineInputSchema(BaseModel):
    sample_id: int = Field(..., description = "Unique identifier for the wine sample")
    #Los puntos quieren decir que no le esta diciendo como tiene que ser?
    fixed_acidity: float = Field(..., description = "Fixed acidity of the wine sample")
    volatile_acidity: float = Filed(..., description = "Volatile acidity of the wine sample")
    citric_acid: float = Field(..., description = "Citric acci")



if __name__ == "__main__"
    mi_contrato = WineInputSchema