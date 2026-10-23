import streamlit as st

st.set_page_config(
    page_title="NYC Taxi Analytics Platform",
    page_icon="🚕",
    layout="wide"
)

# Definición de las 5 páginas
p1 = st.Page("pages/1_Pronostico.py", title="Pronóstico de Demanda", icon="📈", default=True)
p2 = st.Page("pages/2_Segmentacion.py", title="Segmentación de Zonas", icon="🗺️")
p3 = st.Page("pages/3_Decision_Taxis.py", title="Optimización de Flota", icon="🚖")
p4 = st.Page("pages/4_Ficha_Modelo.py", title="Ficha del Modelo", icon="📋")
p5 = st.Page("pages/5_Monitoreo.py", title="Monitoreo del Sistema", icon="📡")

# Estructura del menú lateral
pg = st.navigation({
    "Operaciones": [p1, p3],
    "Análisis & Estrategia": [p2],
    "Gobernanza & MLOps": [p4, p5]
})

pg.run()