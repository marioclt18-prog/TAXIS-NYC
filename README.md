# 🚖 NYC Taxi Analytics Platform — Módulo 2

Plataforma analítica e interactiva para la toma de decisiones en la asignación de flota de taxis amarillos en Nueva York.

## 👥 Integrantes
* Mario Ernesto Mejía Torres

## 🏗️ Arquitectura del Proyecto
* **API (Backend):** Desarrollada en FastAPI y alojada en Render. Proporciona estimaciones de demanda cuantílicas ($p10$ a $p90$).
* **App (Frontend):** Desarrollada en Streamlit (5 páginas) y alojada en Streamlit Community Cloud.

## 📌 Páginas de la Aplicación
1. **📈 Pronóstico de Demanda:** Predicción horaria con bandas de incertidumbre.
2. **🗺️ Segmentación de Zonas:** Clasificación K-Means ($k=4$, Silueta $0.51$) y reducción dimensional con PCA.
3. **🚖 Optimización de Flota:** Modelo económico Newsvendor para balancear costo de oportunidad y exceso de flota.
4. **📋 Ficha del Modelo:** Gobernanza, evaluación del modelo y consideraciones éticas.
5. **📡 Monitoreo MLOps:** Seguimiento del MAE día a día en la semana de prueba.

## 🚀 Ejecución Local

### Backend (API)
```bash
cd API
pip install -r requirements.txt
uvicorn main:app --reload