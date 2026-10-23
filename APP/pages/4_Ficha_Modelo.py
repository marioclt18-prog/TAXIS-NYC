import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📋 Ficha del Modelo (Model Card)")
st.markdown("Especificaciones de gobernanza, evaluación cuantílica y limitaciones éticas del sistema.")

st.markdown("---")

# Rendimiento por tipo de zona
st.subheader("📊 Error del Modelo por Tipo de Zona")
df_error_zona = pd.DataFrame({
    "Tipo de Zona": ["Aeropuertos", "Barrios Periféricos", "Manhattan Central", "Vida Nocturna"],
    "MAE (Viajes/Hora)": [28.4, 6.2, 18.5, 12.1]
})
fig_err = px.bar(df_error_zona, x="MAE (Viajes/Hora)", y="Tipo de Zona", orientation="h", color="Tipo de Zona", title="Error Absoluto Medio (MAE) por Cluster")
st.plotly_chart(fig_err, use_container_width=True)

st.warning("📌 **Nota:** El error es mayor en aeropuertos debido a la alta variabilidad provocada por retrasos de vuelos no incluidos en el modelo.")

st.markdown("---")

st.subheader("⚠️ Limitaciones y Usos No Recomendados")
col_l1, col_l2 = st.columns(2)

with col_l1:
    st.markdown("### 🚫 Usos No Recomendados")
    st.markdown("""
    * **Evaluar o sancionar conductores:** Este modelo estima la demanda agregada de la ciudad, no el desempeño individual.
    * **Recortar servicio en barrios periféricos:** En estas zonas la demanda de taxis amarillos es baja porque operan taxis verdes o aplicaciones. Reducir unidades aumentaría la inequidad en el transporte.
    """)

with col_l2:
    st.markdown("### 🛠️ Limitaciones Técnicas")
    st.markdown("""
    * Entrenado exclusivamente con datos de invierno (Enero 2024).
    * No incorpora eventos meteorológicos extremos o conciertos/eventos masivos repentinos.
    """)

st.markdown("---")

# Interacción exigida por la guía
st.subheader("📬 ¿Te resultó clara esta ficha?")
rating = st.feedback("stars")
if rating is not None:
    st.toast(f"¡Gracias por tu evaluación de {rating + 1} estrellas!", icon="⭐")