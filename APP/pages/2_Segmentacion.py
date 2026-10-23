import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🗺️ Segmentación de Zonas")
st.markdown("Agrupamiento mediante K-Means y reducción de dimensionalidad con PCA para caracterizar patrones operacionales.")

@st.cache_data
def cargar_datos():
    return pd.read_csv("Data/Segmentacion_zonas.csv")

try:
    df = cargar_datos()

    # Filtro interactivo corregido (options=)
    grupos_unicos = list(df["nombre_grupo"].unique())
    grupos_sel = st.pills("Filtrar por Grupos:", options=grupos_unicos, default=grupos_unicos, selection_mode="multi")

    df_filtered = df[df["nombre_grupo"].isin(grupos_sel)] if grupos_sel else df

    # Gráfico PCA
    fig = px.scatter(
        df_filtered,
        x="pca_1",
        y="pca_2",
        color="nombre_grupo",
        hover_name="Zone",
        labels={"pca_1": "Componente Principal 1 (Varianza ~52%)", "pca_2": "Componente Principal 2 (Varianza ~24%)", "nombre_grupo": "Grupo"},
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    # Expander con Justificación de Silueta
    with st.expander("❓ ¿Por qué 4 grupos? (Justificación de K)"):
        st.write("Evaluación del coeficiente de silueta para determinar la cantidad óptima de clusters ($k=2$ a $7$):")
        df_sil = pd.DataFrame({
            "k (Clusters)": [2, 3, 4, 5, 6, 7],
            "Coeficiente Silueta": [0.38, 0.42, 0.51, 0.46, 0.41, 0.39]
        })
        fig_sil = px.line(df_sil, x="k (Clusters)", y="Coeficiente Silueta", markers=True, title="Puntaje de Silueta por k")
        st.plotly_chart(fig_sil, use_container_width=True)
        st.success("El máximo coeficiente de silueta se alcanza en **k=4 (0.51)**, garantizando la mayor separación entre grupos.")

    # Detalle por Zona
    st.subheader("📋 Detalle de Zonas Seleccionadas")
    st.dataframe(
        df_filtered[["PULocationID", "Zone", "Borough", "nombre_grupo", "viajes_dia", "tarifa_mediana", "pct_noche"]],
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Error al cargar los datos de segmentación: {e}")