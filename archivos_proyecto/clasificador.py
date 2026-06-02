import os

# 🔥 EL CÓDIGO DE DESACTIVACIÓN PARA MAC: 
# Le dice al sistema operativo de Apple que no entre en pánico si PyTorch intenta tocar la memoria
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

import torch
# Le ponemos una correa a PyTorch obligándolo a usar estrictamente 1 solo hilo en su núcleo C++
torch.set_num_threads(1)

import pandas as pd
from transformers import pipeline
from tqdm import tqdm

print("🚀 Cargando dataset limpio...")
df = pd.read_csv('ds_lugares_limpio.csv')

print("🤖 Inicializando modelo de IA (Versión ligera para Mac)...")
# Usamos 'distilbart', que es mucho más liviano y pensado para correr en CPUs con poca RAM
classifier = pipeline(
    "zero-shot-classification", 
    model="valhalla/distilbart-mnli-12-1", # Modelo optimizado para RAM limitada
    device="cpu",
    use_fast=False 
)

categorias = ["Trekking", "Naturaleza", "Ciudad", "Multitudes"]

print("🧠 Analizando reseñas (Procesamiento Aislado)...")
resultados = []

# 🔥 TRUCO VITAL: Transformamos la columna de Pandas en una simple lista nativa de Python.
# Esto evita que Pandas y PyTorch se peleen por acceder al mismo bloque de memoria RAM.
textos_puros = df['texto_resena'].astype(str).tolist()

for texto in tqdm(textos_puros):
    try:
        # Procesamos limitando a 500 caracteres
        res = classifier(texto[:500], candidate_labels=categorias)
        diccionario_scores = dict(zip(res['labels'], res['scores']))
        resultados.append(diccionario_scores)
    except Exception as e:
        # En caso de un carácter fantasma, lo saltamos silenciosamente
        resultados.append({"Trekking": 0.0, "Naturaleza": 0.0, "Ciudad": 0.0, "Multitudes": 0.0})

# Unimos todo nuevamente
df_scores = pd.DataFrame(resultados)
df_final = pd.concat([df.reset_index(drop=True), df_scores], axis=1)

print("📊 Calculando el Ranking Definitivo...")
ranking = df_final.groupby('lugar').agg({
    'Trekking': 'mean',
    'Naturaleza': 'mean',
    'Multitudes': 'mean',
    'Ciudad': 'mean',
    'rating': 'mean',
    'latitud': 'first',
    'longitud': 'first'
}).reset_index()

# La fórmula para encontrar aislamiento puro
ranking['Score_Ideal'] = (ranking['Trekking'] + ranking['Naturaleza']) - (ranking['Multitudes'] + ranking['Ciudad'])
ranking = ranking.sort_values(by='Score_Ideal', ascending=False)

ranking.to_csv('ranking_patagonia_ia.csv', index=False)
print("✅ ¡Misión cumplida! El modelo sobrevivió y el ranking está en 'ranking_patagonia_ia.csv'")