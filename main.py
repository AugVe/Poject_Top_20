from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from transformers import pipeline
from math import radians, cos, sin, asin, sqrt

app = FastAPI()

# 1. Carga y limpieza inicial
df_ranking = pd.read_csv('ranking_patagonia_ia_limpio.csv')

# 2. Inicialización del modelo (DistilBART para optimización de RAM)
print("Cargando modelo de intención...")
intent_classifier = pipeline(
    "zero-shot-classification", 
    model="valhalla/distilbart-mnli-12-1", 
    device="cpu", 
    use_fast=False
)

class ViajeRequest(BaseModel):
    cantidad_dias: int
    preferencias: str

def calcular_distancia(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos usando la fórmula de Haversine."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

@app.post("/planificar-itinerario")
def planificar_itinerario(request: ViajeRequest):
    # 1. Detectar intención
    intenciones = intent_classifier(
        request.preferencias, 
        candidate_labels=["Trekking", "Naturaleza", "Ciudad"]
    )
    mejor_categoria = intenciones['labels'][0]
    
    # 2. Filtrado geográfico dinámico (Punto de inicio hardcodeado en Bariloche)
    # El radio crece con los días (100km por día de viaje)
    radio_maximo = request.cantidad_dias * 100 
    punto_inicio = (-41.13, -71.30) 
    
    df_ranking['distancia'] = df_ranking.apply(
        lambda row: calcular_distancia(punto_inicio[0], punto_inicio[1], row['latitud'], row['longitud']), axis=1
    )
    
    # Filtramos por radio
    itinerario = df_ranking[df_ranking['distancia'] <= radio_maximo].copy()
    
    # Si el filtro es muy restrictivo, usamos todo el dataset como respaldo
    if len(itinerario) < request.cantidad_dias:
        itinerario = df_ranking.copy()

    # 3. Ordenamiento inteligente (Prioridad + Score Ideal)
    mapeo = {"Trekking": "Trekking", "Naturaleza": "Naturaleza", "Ciudad": "Ciudad"}
    columna_orden = mapeo.get(mejor_categoria, "Score_Ideal")
    
    itinerario['Ranking_Final'] = (itinerario[columna_orden] * 0.4) + (itinerario['Score_Ideal'] * 0.6)
    itinerario = itinerario.sort_values(by='Ranking_Final', ascending=False).head(request.cantidad_dias)
    
    # 4. Limpieza final para formato JSON
    resultado_limpio = itinerario.replace([np.nan, np.inf, -np.inf], None).to_dict(orient='records')
    
    return {
        "prioridad_detectada": mejor_categoria,
        "itinerario": resultado_limpio
    }
