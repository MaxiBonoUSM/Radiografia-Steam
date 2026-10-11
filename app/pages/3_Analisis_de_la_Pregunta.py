"""
Pagina 3: Analisis de la Pregunta.

Proposito analitico: responder "que hemos aprendido hasta ahora sobre nuestra
pregunta". Conecta el EDA con la problematica: estudia relaciones entre los
predictores X y el objetivo Y, el componente temporal T y resume los hallazgos
preliminares.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import encabezado, obtener_datos, aplicar_filtros, COLORES  # noqa: E402
from src import viz  # noqa: E402

st.set_page_config(page_title="Analisis de la Pregunta", page_icon="chart", layout="wide")

encabezado("3. Analisis de la Pregunta", "Que hemos aprendido hasta ahora")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)

# Relacion entre X e Y
st.subheader("Relaciones entre caracteristicas (X) y recepcion (Y)")

col_a, col_b = st.columns(2)
with col_a:
    tendencia = st.toggle("Mostrar linea de tendencia", value=True)
    st.plotly_chart(viz.precio_vs_recepcion(datos_f, con_tendencia=tendencia),
                    use_container_width=True)
    st.caption(
        "Observacion: evalue si existe una relacion clara entre precio y recepcion, "
        "y si parece lineal o no. El tamanio del punto codifica el volumen de resenas."
    )
with col_b:
    st.plotly_chart(viz.recepcion_por_comunidad(datos_f), use_container_width=True)
    st.caption(
        "Observacion: compara la recepcion de juegos con y sin funcionalidades "
        "comunitarias (multijugador o Steam Workshop)."
    )

st.plotly_chart(viz.idiomas_vs_popularidad(datos_f), use_container_width=True)
st.caption(
    "Observacion: relacion entre el numero de idiomas soportados y la mediana de "
    "resenas, usada como aproximacion a la popularidad."
)

st.divider()

# Componente temporal
st.subheader("Componente temporal (T)")
st.plotly_chart(viz.evolucion_recepcion(datos_f), use_container_width=True)
st.markdown(
    f"<p style='color:{COLORES['gris']}'>Interpretacion: la evolucion de la recepcion "
    "mediana por anio permite ver si los juegos mas recientes tienden a ser mejor o "
    "peor valorados. Recuerde que las metricas acumuladas favorecen a los juegos mas "
    "antiguos.</p>",
    unsafe_allow_html=True,
)

st.divider()

# Vision de conjunto
st.subheader("Vision de conjunto")
st.plotly_chart(viz.matriz_correlacion(datos_f), use_container_width=True)
st.caption(
    "La matriz de correlacion de Spearman resume que variables numericas se mueven "
    "juntas. Se usa para orientar el analisis, no como conclusion automatica."
)

st.divider()

# Sintesis de hallazgos
st.subheader("Hallazgos preliminares")
st.markdown(
    """
Esta pagina reune la evidencia para pasar de "estos son nuestros datos" a "esto
es lo que hemos aprendido". A partir de las visualizaciones anteriores, el equipo
documenta:

- que variables parecen tener mayor relacion con la recepcion;
- si las relaciones observadas son lineales o no;
- que diferencias entre grupos resultan relevantes;
- que comportamiento temporal se observa;
- que limita las conclusiones por ahora (sesgo de supervivencia, metricas acumuladas).

Estos hallazgos son la base del Avance 3.
"""
)
