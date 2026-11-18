from fastapi import APIRouter

from app.schemas.prestamo import PrediccionSalida, PrestamoEntrada
from app.services.modelo import predecir

router = APIRouter()


# TODO: POST /predict (entrada PrestamoEntrada, salida PrediccionSalida)

router = APIRouter() #Crea un router donde definimos las rutas de nuestra API

#Creamos una ruta (llamada /predict) y se le indica cómo debe ser la respuesta
@router.post("/predict", response_model=PrediccionSalida)
def predict(entrada: PrestamoEntrada):
    return predecir(entrada)

#Los dos puntos : indican que entrada debe ser de tipo PrestamoEntrada.
#Cuando FastAPI recibe una petición, ve esa anotación y utiliza Pydantic 
# para validar los datos antes de ejecutar la función predict().