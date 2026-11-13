import joblib

from app.config import MODEL_PATH
from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada

# Orden en el que el modelo espera las variables
VARIABLES = [
    "edad",
    "ingresos_mensuales",
    "importe_prestamo",
    "plazo_meses",
    "antiguedad_laboral_anios",
    "impagos_previos",
]

# TODO: cargar el modelo joblib una sola vez, al importar el modulo
# TODO: funcion decidir(probabilidad) -> "aprobar", "revisar" o "rechazar" (umbrales en el enunciado)
# TODO: funcion predecir(entrada) -> PrediccionSalida, usando VARIABLES para ordenar los valores

model = joblib.load(MODEL_PATH)


def decidir(probabilidad: float) -> str:
    if probabilidad < 0.2:
        return "aprobar"
    elif probabilidad < 0.5:
        return "revisar"
    else: 
        return "rechazar"
    
def predecir(entrada: PrestamoEntrada) -> PrediccionSalida:
    #Obtener los datos en el orden correcto
    valores = [getattr(entrada, variable) for variable in VARIABLES]
    #Calcular la probabilidad de impago
    probabilidad = float(model.predict_proba([valores])[0][1])
    #Obtener la decisión
    decision = decidir(probabilidad)
    #Devolver la predicción
    return PrediccionSalida(
        probabilidad_impago = probabilidad,
        decision = decision
    )
    