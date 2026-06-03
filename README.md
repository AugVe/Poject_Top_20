# 🏔️ Planificador IA Patagonia - Motor de Itinerarios

Una aplicación web *Full-Stack* ligera y rápida que genera itinerarios de viaje personalizados en la Patagonia argentina mediante procesamiento de lenguaje natural y cálculos de distancia geolocalizados.

El algoritmo central fue diseñado específicamente para resolver esos "cuellos de botella" logísticos y superposiciones de calendario que suelen complicar la planificación de viajes largos. Al calcular distancias dinámicas y filtrar multitudes, el sistema garantiza que el itinerario final sea logísticamente realizable, ya sea recorriendo los alrededores inmediatos o trazando rutas más extensas que conecten puntos clave del sur argentino, como Bariloche, El Chaltén y Ushuaia, dependiendo del tiempo disponible.

## 🚀 Características Principales

* **Clasificación de Intención (Zero-RAM):** Analiza las preferencias del usuario (texto libre) mediante un clasificador heurístico optimizado para consumir 0 MB de memoria RAM, ideal para despliegues en servidores gratuitos (Free Tiers).
* **Radio Geográfico Dinámico:** Utiliza la fórmula de *Haversine* para expandir o contraer el radio de búsqueda geográfico en función de la cantidad de días de viaje seleccionados por el usuario.
* **Filtro Multi-Criterio:** Pondera las recomendaciones cruzando variables como la preferencia de aislamiento (Naturaleza vs. Multitudes) y las distancias físicas entre los puntos.
* **Single Page Application (SPA):** Frontend integrado directamente en el servidor backend sin problemas de CORS, proporcionando una experiencia de usuario fluida y reactiva.

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.12, FastAPI, Uvicorn.
* **Procesamiento de Datos:** Pandas, NumPy, Math (Haversine).
* **Frontend:** Vanilla HTML5, CSS3, JavaScript (Fetch API).
* **Despliegue (Deploy):** Configurado para funcionar nativamente en Render.

## 📂 Estructura del Proyecto
```
/
├── main.py                          # Motor de la API y lógica de rutas (FastAPI)
├── index.html                       # Interfaz gráfica (SPA)
├── ranking_patagonia_ia_limpio.csv  # Dataset pre-procesado de destinos y scores
├── requirements.txt                 # Dependencias del proyecto
└── .gitignore                       # Archivos ignorados por el control de versiones
```

## 💻 Instalación y Uso Local

Si deseas correr este proyecto en tu propia máquina, sigue estos pasos:

1. Clonar el repositorio:
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

2. Crear y activar un entorno virtual:
python3 -m venv venv
source venv/bin/activate

3. Instalar dependencias:
pip install -r requirements.txt

4. Ejecutar el servidor de desarrollo:
uvicorn main:app --reload

5. Abre tu navegador y dirígete a http://localhost:8000

## ☁️ Despliegue en la Nube

Este proyecto está optimizado para ser desplegado en Render como un *Web Service*. 
* Build Command: pip install -r requirements.txt
* Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT

Nota: No requiere modelos pesados de Machine Learning locales, evitando errores de límite de memoria (OOM).

## 🤝 Próximos Pasos (Roadmap)
* [ ] Integración de un mapa interactivo (Leaflet/Folium) en el frontend.
* [ ] Expansión del dataset (.csv) mediante web scraping automatizado de plataformas de reseñas.
* [ ] Inclusión de variables de clima y estacionalidad en la función de puntuación.