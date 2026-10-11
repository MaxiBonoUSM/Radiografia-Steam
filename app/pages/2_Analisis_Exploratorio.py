"""
Pagina 2: Analisis Exploratorio.

Proposito analitico: responder "como se comportan nuestros datos".
Concentra el analisis univariado y las primeras comparaciones entre grupos:
distribucion de la variable objetivo, distribucion de precios, frecuencia de
generos y recepcion comparada por genero. Incluye estadisticas descriptivas.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import encabezado, obtener_datos, aplicar_filtros, COLORES  # noqa: E402
from src import data_loading, viz  # noqa: E402

st.set_page_config(page_title="Analisis Exploratorio", page_icon="chart", layout="wide")

encabezado("2. Analisis Exploratorio", "Como se comportan nuestros datos")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)

# Analisis univariado
st.subheader("Analisis univariado")

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(viz.distribucion_y(datos_f), use_container_width=True)
    st.caption(
        "Observacion: la distribucion de la proporcion de positivas suele estar "
        "concentrada en valores altos. Interprete donde cae la mediana y que tan "
        "larga es la cola de juegos mal recibidos."
    )
with col_b:
    log_y = st.toggle("Eje vertical logaritmico", value=True,
                      help="Util porque los precios estan muy sesgados hacia valores bajos.")
    st.plotly_chart(viz.distribucion_precio(datos_f, log_y=log_y),
                    use_container_width=True)
    st.caption(
        "Observacion: la mayoria de los juegos se concentra en precios bajos o "
        "gratuitos. La escala logaritmica permite ver la cola de precios altos."
    )

st.plotly_chart(viz.frecuencia_generos(datos_f), use_container_width=True)
st.caption("Observacion: identifica que generos dominan el catalogo filtrado.")

st.divider()

# Comparacion entre grupos
st.subheader("Comparacion entre grupos")
st.plotly_chart(viz.recepcion_por_genero(datos_f), use_container_width=True)
st.markdown(
    f"<p style='color:{COLORES['gris']}'>Interpretacion: el orden de los generos por "
    "mediana de recepcion sugiere en cuales la valoracion de los jugadores tiende a "
    "ser mas alta o mas dispersa.</p>",
    unsafe_allow_html=True,
)

st.divider()

# Estadisticas descriptivas
st.subheader("Estadisticas descriptivas")
st.dataframe(
    data_loading.estadisticas_descriptivas(datos_f),
    use_container_width=True,
)
st.caption(
    "Las estadisticas se interpretan junto a los graficos. Una tabla por si sola "
    "no constituye un analisis; aqui respaldan las observaciones anteriores."
)
