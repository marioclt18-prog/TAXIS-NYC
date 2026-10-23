import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📡 Monitoreo Día a Día (Semana de Prueba)")
st.markdown("Seguimiento del error del modelo entre el 25 y el 31 de enero de 2024 con alertas de umbral.")

st.sidebar.header("⚙️ Umbral de Alerta")
umbral_mae = st.sidebar.slider("Límite Máximo MAE Tolerable (Viajes):", min_value=10, max_value=30, value=15)

# Datos de la semana de prueba
df_eval = pd.DataFrame({
    "Fecha": ["2024-01-25", "2024-01-26", "2024-01-27", "2024-01-28", "2024-01-29", "2024-01-30", "2024-01-31"],
    "Día": ["Jueves", "Viernes", "Sábado", "Domingo", "Lunes", "Martes", "Miércoles"],
    "MAE_Modelo": [11.2, 12.8, 16.4, 14.1, 10.9, 11.5, 13.2],
    "MAE_Baseline": [12.5, 14.1, 18.2, 15.0, 11.8, 12.0, 14.5]
})

fig = px.line(df_eval, x="Fecha", y=["MAE_Modelo", "MAE_Baseline"], markers=True, title="MAE Diarios en Semana de Prueba")
fig.add_hline(y=umbral_mae, line_dash="dash", line_color="red", annotation_text=f"Umbral Alerta ({umbral_mae})")
st.plotly_chart(fig, use_container_width=True)

# Evaluación de alertas
dias_alerta = df_eval[df_eval["MAE_Modelo"] > umbral_mae]
if not dias_alerta.empty:
    st.error(f"⚠️ **Alerta MLOps:** En {len(dias_alerta)} día(s) se superó el umbral de error tolerado ({umbral_mae} viajes). Revisa el comportamiento en fin de semana.")
else:
    st.success("✅ **Sistema Estilizado:** El error se mantuvo dentro de los límites operativos aceptables durante toda la semana de prueba.")