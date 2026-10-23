from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
import xgboost as xgb
import os

app = FastAPI(title="NYC Taxi Forecasting API", version="1.0")

# 1. Rutas locales de los archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMANDA_PATH = os.path.join(BASE_DIR, "demanda.parquet")
MODELO_PATH = os.path.join(BASE_DIR, "modelo_pronostico.ubj")

# 2. Cargar datos y modelo en memoria
demanda_df = pd.read_parquet(DEMANDA_PATH)
model = xgb.XGBRegressor()
model.load_model(MODELO_PATH)

FEATURES = ['lag_24', 'lag_48', 'lag_167', 'lag_168', 'lag_169', 'media_dia_ant', 'num_hora', 'dia_semana', 'feriado', 'zona']
CUANTILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# Endpoint 1: Verificación de estado
@app.get("/")
def read_root():
    return {"status": "ok", "message": "API de Pronóstico de Taxis NYC en línea"}

# Endpoint 3: Obtener pronóstico de 24 horas para una zona y fecha
@app.get("/pronostico")
def get_pronostico(zona_id: int = Query(...), fecha: str = Query(...)):
    # 1. Filtrar las 24 horas solicitadas
    filas = demanda_df[
        (demanda_df['PULocationID'] == zona_id) & 
        (demanda_df['hora'].dt.strftime('%Y-%m-%d') == fecha)
    ].sort_values('num_hora').copy()

    if filas.empty:
        raise HTTPException(status_code=404, detail="No hay datos para esa zona o fecha")

    # Asegurar que la columna 'zona' exista y sea de tipo categórico
    if 'zona' not in filas.columns:
        filas['zona'] = filas['PULocationID']
    filas['zona'] = filas['zona'].astype('category')

    # 2. Predecir los cuantiles con el modelo
    X = filas[FEATURES]
    preds = model.predict(X)
    preds_sorted = np.sort(preds, axis=1)  # Ordenar cuantiles cruzados

    # 3. Construir la respuesta en formato JSON
    horas_payload = []
    for idx, (_, row) in enumerate(filas.iterrows()):
        val_real = float(row['viajes']) if str(row['hora'].date()) != "2024-02-01" else None
        hace_una_semana = float(row['lag_168']) if not pd.isna(row['lag_168']) else 0.0
        
        c_dict = {f"p{int(q*100)}": float(np.round(preds_sorted[idx, i], 1)) for i, q in enumerate(CUANTILES)}

        horas_payload.append({
            "hora": int(row['num_hora']),
            "real": val_real,
            "hace_una_semana": hace_una_semana,
            "cuantiles": c_dict
        })

    return {
        "zona_id": zona_id,
        "fecha": fecha,
        "horas": horas_payload
    }