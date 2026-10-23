import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Manejo seguro de secrets para local y nube
try:
    API_BASE_URL = st.secrets["API_URL"]
except Exception:
    API_BASE_URL = "http://127.0.0.1:8000"

st.title("🚖 ¿Cuántos taxis enviar?")
st.markdown("Determinación del nivel óptimo de flota balanceando el costo de oportunidad y el costo de exceso de capacidad.")

# Carga de Metadatos
@st.cache_data(ttl=3600)
def obtener_info_api():
    try:
        res = requests.get(f"{API_BASE_URL}/info", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

info = obtener_info_api()
zonas_disponibles = info.get("zonas", [132, 230, 161, 142, 236]) if info else [132, 230, 161, 142, 236]
fechas_disponibles = info.get("fechas", ["2024-01-25", "2024-01-26", "2024-01-27", "2024-02-01"]) if info else ["2024-01-25", "2024-01-26", "2024-01-27", "2024-02-01"]

# Selección de Zona y Fecha
col_z, col_f = st.columns(2)
with col_z:
    zona_sel = st.selectbox("Zona:", zonas_disponibles)
with col_f:
    fecha_sel = st.select_slider("Fecha:", options=fechas_disponibles)

st.markdown("---")

# Fragmento para actualización fluida de controles de costo
@st.fragment
def renderizar_optimizacion():
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        costo_ocioso = st.slider("Costo de un taxi sin pasajero / hora (USD):", min_value=5, max_value=50, value=10, step=5)
    with col_c2:
        costo_perdido = st.slider("Costo de un pasajero no atendido (USD):", min_value=10, max_value=100, value=40, step=5)

    # Cálculo del cuantil óptimo (Newsvendor)
    q_opt = costo_perdido / (costo_perdido + costo_ocioso)
    cuantil_num = int(round(q_opt * 10) * 10)
    cuantil_num = max(10, min(90, cuantil_num))
    clave_cuantil = f"p{cuantil_num}"

    ratio = costo_perdido / costo_ocioso
    st.info(f"💡 Perder un pasajero cuesta **{ratio:.1f} veces** lo que cuesta un taxi ocioso. La regla óptima es cubrir el **cuantil {cuantil_num}% ({clave_cuantil})** de la demanda.")

    st.latex(r"\text{cuantil óptimo} = \frac{C_{\text{perdida}}}{C_{\text{perdida}} + C_{\text{ocioso}}} = \frac{" + f"{costo_perdido}" + r"}{" + f"{costo_perdido} + {costo_ocioso}" + r"} = " + f"{q_opt:.2f}")

    # Consulta a la API
    try:
        resp = requests.get(f"{API_BASE_URL}/pronostico", params={"zona_id": zona_sel, "fecha": fecha_sel}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            filas = []
            for h in data["horas"]:
                c_dict = h.get("cuantiles", {})
                filas.append({
                    "hora": h["hora"],
                    "real": h.get("real"),
                    "hace_una_semana": h.get("hace_una_semana", 0),
                    "p50": c_dict.get("p50", 0),
                    "recomendacion": c_dict.get(clave_cuantil, c_dict.get("p50", 0))
                })
            df = pd.DataFrame(filas)

            # Gráfico de Asignación
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df["hora"], y=df["recomendacion"], name=f"Recomendación ({clave_cuantil})", marker_color="#1f77b4"))
            fig.add_trace(go.Scatter(x=df["hora"], y=df["p50"], name="Pronóstico Central (p50)", mode="lines", line=dict(color="#ff7f0e", dash="dash")))
            
            if df["real"].notnull().any():
                fig.add_trace(go.Scatter(x=df["hora"], y=df["real"], name="Demanda Real", mode="markers+lines", marker=dict(color="red", size=6)))

            fig.update_layout(
                title=f"Plan de Taxis Recomendado vs Pronóstico Central — Zona {zona_sel}",
                xaxis_title="Hora del Día",
                yaxis_title="Taxis / Viajes",
                template="plotly_white",
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)

            # Comparación de Costos
            if df["real"].notnull().all():
                st.subheader("💰 Evaluación Financiera del Día")
                
                def calcular_costo_total(enviados_series, real_series):
                    exceso = np.maximum(enviados_series - real_series, 0) * costo_ocioso
                    deficit = np.maximum(real_series - enviados_series, 0) * costo_perdido
                    return (exceso + deficit).sum()

                costo_rec = calcular_costo_total(df["recomendacion"], df["real"])
                costo_p50 = calcular_costo_total(df["p50"], df["real"])
                costo_base = calcular_costo_total(df["hace_una_semana"], df["real"])

                m1, m2, m3 = st.columns(3)
                m1.metric("Recomendación Óptima", f"${costo_rec:,.0f}")
                m2.metric("Pronóstico Central (p50)", f"${costo_p50:,.0f}", delta=f"{((costo_p50-costo_rec)/costo_rec)*100:+.1f}% costo", delta_color="inverse")
                m3.metric("Hace 1 Semana (Baseline)", f"${costo_base:,.0f}", delta=f"{((costo_base-costo_rec)/costo_rec)*100:+.1f}% costo", delta_color="inverse")

            # Botón de Descarga
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar plan de taxis por hora (CSV)",
                data=csv_data,
                file_name=f"plan_taxis_zona_{zona_sel}_{fecha_sel}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error de comunicación con la API: {e}")

renderizar_optimizacion()