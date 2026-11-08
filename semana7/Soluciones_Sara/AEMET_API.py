
import os
import requests# Obtenemos la clave de AEMET desde una variable de entorno
from dotenv import load_dotenv

#Cargamos las variables del archivo .env
load_dotenv()

#Obtenemos nuestra clave de acceso a AEMET
api_key = os.environ["AEMET_API_KEY"]



#Parámetros que enviamos en la petición para auteticarnos
params = {
    "api_key": api_key
}

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"


response = requests.get(url, params=params)
#Código para ver si ha tenido exito (200)
print(response.status_code)
print(response.json())

idema = "3194U"
fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"
url_diaria= f'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}'
respuesta = requests.get(url_diaria, params=params)
print(respuesta.status_code)
print(respuesta.json())



#Para ver los datos metereológicos:
# Obtenemos la URL que contiene los datos climatológicos
url_datos = respuesta.json()["datos"]
# Descargamos los datos de la estación
datos = requests.get(url_datos)
# Mostramos los datos climatológicos diarios
print(datos.json())