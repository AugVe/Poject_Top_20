from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

app = FastAPI()

@app.get("/")
def mostrar_interfaz():
    return FileResponse("index.html")

# 1. Carga de datos
df_ranking = pd.read_csv('ranking_patagonia_ia_limpio.csv')

class ViajeRequest(BaseModel):
    cantidad_dias: int
    preferencias: str

# 2. Clasificador Ligero (Reemplaza a HuggingFace para no consumir RAM)
def detectar_intencion_ligera(texto: str):
    texto = texto.lower()
    if any(palabra in texto for palabra in ["ciudad", "compras", "urbano", "hotel", "ruido", "gente"]):
        return "Ciudad"
    elif any(palabra in texto for palabra in ["naturaleza", "silencio", "virgen", "aislado", "paz"]):
        return "Naturaleza"
    else:
        return "Trekking" # Opción por defecto o si menciona montaña/trekking

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

@app.post("/planificar-itinerario")
def planificar_itinerario(request: ViajeRequest):
    # Usamos nuestro clasificador de 0 RAM
    mejor_categoria = detectar_intencion_ligera(request.preferencias)
    
    radio_maximo = request.cantidad_dias * 100 
    punto_inicio = (-41.13, -71.30) 
    
    df_ranking['distancia'] = df_ranking.apply(
        lambda row: calcular_distancia(punto_inicio[0], punto_inicio[1], row['latitud'], row['longitud']), axis=1
    )
    
    itinerario = df_ranking[df_ranking['distancia'] <= radio_maximo].copy()
    
    if len(itinerario) < request.cantidad_dias:
        itinerario = df_ranking.copy()

    mapeo = {"Trekking": "Trekking", "Naturaleza": "Naturaleza", "Ciudad": "Ciudad"}
    columna_orden = mapeo.get(mejor_categoria, "Score_Ideal")
    
    itinerario['Ranking_Final'] = (itinerario[columna_orden] * 0.4) + (itinerario['Score_Ideal'] * 0.6)
    itinerario = itinerario.sort_values(by='Ranking_Final', ascending=False).head(request.cantidad_dias)
    
    resultado_limpio = itinerario.replace([np.nan, np.inf, -np.inf], None).to_dict(orient='records')
    
    return {
        "prioridad_detectada": mejor_categoria,
        "itinerario": resultado_limpio
    }