import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_BASE_URL = "http://127.0.0.1:8000"

st.title("📈 Pronóstico de Demanda con Incertidumbre")
st.markdown("Consulta las predicciones horarias con intervalos de confianza cuantílicos ($p10$-$p90$).")

# ---------------------------------------------------------
# Función con Cache y Conexión Segura
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def obtener_info_api():
    try:
        res = requests.get(f"{API_BASE_URL}/info", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None

info = obtener_info_api()

# Fallback de datos si la API aún no devuelve metadatos
zonas_disponibles = info.get("zonas", [132, 230, 161, 142, 236]) if info else [132, 230, 161, 142, 236]
fechas_disponibles = info.get("fechas", ["2024-01-25", "2024-01-26", "2024-01-27", "2024-01-28", "2024-01-29", "2024-01-30", "2024-01-31", "2024-02-01"]) if info else ["2024-01-25", "2024-01-26", "2024-01-27"]

# ---------------------------------------------------------
# Barra Lateral y Filtros con Componentes Avanzados
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de Consulta")

zona_sel = st.sidebar.selectbox("Zona ID:", zonas_disponibles)
fecha_sel = st.sidebar.selectbox("Fecha:", fechas_disponibles)

st.sidebar.markdown("---")
st.sidebar.markdown("**Visualización de Cuantiles:**")
cuantiles_vis = st.sidebar.pills("Resaltar Banda:", ["p10 - p90", "Solo P50"], default="p10 - p90")

st.sidebar.info("💡 La sombra representa el intervalo de incertidumbre del 80% ($p10$ a $p90$).")

# ---------------------------------------------------------
# Ejecución y Consulta con st.status
# ---------------------------------------------------------
if st.sidebar.button("Consultar Pronóstico", type="primary", use_container_width=True):
    with st.status("Conectando con el backend de pronóstico...", expanded=True) as status:
        st.write("Enviando petición a la API...")
        try:
            resp = requests.get(
                f"{API_BASE_URL}/pronostico",
                params={"zona_id": zona_sel, "fecha": fecha_sel},
                timeout=120
            )
            
            if resp.status_code == 200:
                status.update(label="¡Pronóstico generado exitosamente!", state="complete", expanded=False)
                data = resp.json()
                
                # Formatear datos
                df = pd.DataFrame([
                    {
                        "hora": int(h["hora"]),
                        "real": h["real"],
                        "hace_una_semana": h["hace_una_semana"],
                        **h["cuantiles"]
                    }
                    for h in data["horas"]
                ])
                
                # --- MÉTRICAS CLAVE ---
                col1, col2, col3, col4 = st.columns(4)
                
                total_p50 = int(df["p50"].sum())
                hora_pico = int(df.loc[df["p50"].idxmax(), "hora"])
                total_semana = int(df["hace_una_semana"].sum())
                diff_semana = total_p50 - total_semana
                
                col1.metric("Demanda Estimada (P50)", f"{total_p50:,} viajes")
                col2.metric("Hora Pico Estimada", f"{hora_pico:02d}:00 hs")
                col3.metric("Semana Pasada", f"{total_semana:,} viajes")
                col4.metric("Diferencia vs Histórico", f"{diff_semana:+,} viajes", delta_color="normal")
                
                st.markdown("---")
                
                # --- GRÁFICO CON PLOTLY ---
                fig = go.Figure()
                
                if cuantiles_vis == "p10 - p90":
                    fig.add_trace(go.Scatter(
                        x=df["hora"], y=df["p90"], mode='lines', line=dict(width=0), showlegend=False, name='p90'
                    ))
                    fig.add_trace(go.Scatter(
                        x=df["hora"], y=df["p10"], mode='lines', line=dict(width=0),
                        fill='tonexty', fillcolor='rgba(31, 119, 180, 0.18)', name='Incertidumbre (p10-p90)'
                    ))

                fig.add_trace(go.Scatter(
                    x=df["hora"], y=df["p50"], mode='lines+markers', name='Predicción Central (P50)',
                    line=dict(color='#1f77b4', width=3)
                ))

                fig.add_trace(go.Scatter(
                    x=df["hora"], y=df["hace_una_semana"], mode='lines', name='Hace 1 Semana (Baseline)',
                    line=dict(color='gray', dash='dash')
                ))

                if df["real"].notna().any():
                    fig.add_trace(go.Scatter(
                        x=df["hora"], y=df["real"], mode='lines+markers', name='Demanda Real',
                        line=dict(color='#d62728', width=2.5)
                    ))

                fig.update_layout(
                    title=dict(text=f"Pronóstico Horario — Zona {zona_sel} ({fecha_sel})", font=dict(size=18)),
                    xaxis=dict(title="Hora del Día", dtick=2),
                    yaxis=dict(title="Cantidad de Viajes"),
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white",
                    height=450
                )

                st.plotly_chart(fig, use_container_width=True)

                # --- TABLA INTERACTIVA CON COLUMN_CONFIG ---
                with st.expander("📊 Ver Tabla de Datos y Cuantiles Detallados"):
                    st.dataframe(
                        df,
                        column_config={
                            "hora": st.column_config.NumberColumn("Hora", format="%d:00 hs"),
                            "p10": st.column_config.NumberColumn("Cuantil P10", format="%d"),
                            "p50": st.column_config.NumberColumn("Cuantil P50 (Mediana)", format="%d"),
                            "p90": st.column_config.NumberColumn("Cuantil P90", format="%d"),
                            "hace_una_semana": st.column_config.NumberColumn("Histórico 1 Sem", format="%d"),
                            "real": st.column_config.NumberColumn("Real", format="%d")
                        },
                        use_container_width=True,
                        hide_index=True
                    )

            else:
                status.update(label="Error en la API", state="error")
                st.error(f"La API respondió con estado {resp.status_code}.")

        except requests.exceptions.Timeout:
            status.update(label="Tiempo de espera agotado", state="error")
            st.error("La API tardó demasiado en responder (posiblemente despertando en Render). Intenta de nuevo.")
        except Exception as e:
            status.update(label="Error de conexión", state="error")
            st.error(f"No se pudo conectar a la API: {e}")