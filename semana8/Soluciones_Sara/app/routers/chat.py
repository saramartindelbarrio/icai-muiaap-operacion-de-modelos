from fastapi import APIRouter, Depends

from app.schemas.chat import ChatEntrada, ChatSalida
from app.services.llm import get_llm
from app.services.orquestador import responder

router = APIRouter()


# TODO: POST /chat (entrada ChatEntrada, salida ChatSalida). Recibe el LLM con Depends(get_llm)
@router.post("/chat", response_model=ChatSalida)
def chat(entrada: ChatEntrada, llm=Depends(get_llm)):
    return responder(entrada.mensajes, llm) # LE MANDAMOS LOS MENSAJES DE LA CONVER Y EL MODELO DE LENGUAJE QUE NOS HA PROPORCIONADO FASTAPI

#Aqui le estas diciendo que cree una ruta /chat que recibe peticiones POST, que quieres que cumpla el formato ChatSalida
#Se valida que la entrada sea ChatEntrada
#FastAPI, antes de ejecutar esta función, llama a get_llm() y dame el LLM que devuelve.